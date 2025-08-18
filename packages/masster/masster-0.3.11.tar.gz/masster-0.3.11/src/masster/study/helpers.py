from __future__ import annotations

import os

import numpy as np
import pandas as pd
import polars as pl

from tqdm import tqdm


def get_chrom(self, uids=None, samples=None):
    # Check if consensus_df is empty or doesn't have required columns
    if self.consensus_df.is_empty() or "consensus_uid" not in self.consensus_df.columns:
        self.logger.error("No consensus data found. Please run merge() first.")
        return None

    ids = self._get_consensus_uids(uids)
    sample_uids = self._get_sample_uids(samples)

    if self.consensus_map is None:
        self.logger.error("No consensus map found.")
        return None

    # Pre-filter all DataFrames to reduce join sizes
    filtered_consensus_mapping = self.consensus_mapping_df.filter(
        pl.col("consensus_uid").is_in(ids),
    )

    # Get feature_uids that we actually need
    relevant_feature_uids = filtered_consensus_mapping["feature_uid"].to_list()

    self.logger.debug(
        f"Filtering features_df for {len(relevant_feature_uids)} relevant feature_uids.",
    )
    # Pre-filter features_df to only relevant features and samples
    filtered_features = self.features_df.filter(
        pl.col("feature_uid").is_in(relevant_feature_uids) & pl.col("sample_uid").is_in(sample_uids),
    ).select([
        "feature_uid",
        "chrom",
        "rt",
        "rt_original",
        "sample_uid",
    ])

    # Pre-filter samples_df
    filtered_samples = self.samples_df.filter(
        pl.col("sample_uid").is_in(sample_uids),
    ).select(["sample_uid", "sample_name"])

    # Perform a three-way join to get all needed data
    self.logger.debug("Joining DataFrames to get complete chromatogram data.")
    df_combined = (
        filtered_consensus_mapping.join(
            filtered_features,
            on="feature_uid",
            how="inner",
        )
        .join(filtered_samples, on="sample_uid", how="inner")
        .with_columns(
            (pl.col("rt") - pl.col("rt_original")).alias("rt_shift"),
        )
    )

    # Update chrom objects with rt_shift efficiently
    self.logger.debug("Updating chromatogram objects with rt_shift values.")
    chrom_data = df_combined.select(["chrom", "rt_shift"]).to_dict(as_series=False)
    for chrom_obj, rt_shift in zip(chrom_data["chrom"], chrom_data["rt_shift"]):
        if chrom_obj is not None:
            chrom_obj.rt_shift = rt_shift

    # Get all unique combinations for complete matrix
    all_consensus_uids = sorted(df_combined["consensus_uid"].unique().to_list())
    all_sample_names = sorted(df_combined["sample_name"].unique().to_list())

    # Create a mapping dictionary for O(1) lookup instead of O(n) filtering
    self.logger.debug("Creating lookup dictionary for chromatogram objects.")
    chrom_lookup = {}
    for row in df_combined.select([
        "consensus_uid",
        "sample_name",
        "chrom",
    ]).iter_rows():
        key = (row[0], row[1])  # (consensus_uid, sample_name)
        chrom_lookup[key] = row[2]  # chrom object

    # Build pivot data efficiently using the lookup dictionary
    pivot_data = []
    total_iterations = len(all_consensus_uids)
    progress_interval = max(1, total_iterations // 10)  # Show progress every 10%

    for i, consensus_uid in enumerate(all_consensus_uids):
        if i % progress_interval == 0:
            progress_percent = (i / total_iterations) * 100
            self.logger.debug(
                f"Building pivot data: {progress_percent:.0f}% complete ({i}/{total_iterations})",
            )

        row_data = {"consensus_uid": consensus_uid}
        for sample_name in all_sample_names:
            key = (consensus_uid, sample_name)
            row_data[sample_name] = chrom_lookup.get(key, None)
        pivot_data.append(row_data)

    self.logger.debug(
        f"Building pivot data: 100% complete ({total_iterations}/{total_iterations})",
    )

    # Create Polars DataFrame with complex objects
    df2_pivoted = pl.DataFrame(pivot_data)

    # Return as Polars DataFrame (can handle complex objects like Chromatogram)
    return df2_pivoted


def set_folder(self, folder):
    """
    Set the folder for saving and loading files.
    """
    if not os.path.exists(folder):
        os.makedirs(folder)
    self.folder = folder


def align_reset(self):
    if self.alignment_ref_index is None:
        return
    self.logger.debug("Resetting alignment.")
    # iterate over all feature maps and set RT to original RT
    for feature_map in self.features_maps:
        for feature in feature_map:
            rt = feature.getMetaValue("original_RT")
            if rt is not None:
                feature.setRT(rt)
                feature.removeMetaValue("original_RT")
    self.alignment_ref_index = None


# TODO I don't get this param
def get_consensus(self, quant="chrom_area"):
    if self.consensus_df is None:
        self.logger.error("No consensus map found.")
        return None

    # Convert Polars DataFrame to pandas for this operation since the result is used for export
    df1 = self.consensus_df.to_pandas().copy()

    # set consensus_id as uint64
    df1["consensus_id"] = df1["consensus_id"].astype("uint64")
    # set consensus_id as index
    df1.set_index("consensus_uid", inplace=True)
    # sort by consensus_id
    df1 = df1.sort_index()

    df2 = self.get_consensus_matrix(quant=quant)
    # sort df2 row by consensus_id
    df2 = df2.sort_index()
    # merge df and df2 on consensus_id
    df = pd.merge(df1, df2, left_index=True, right_index=True, how="left")

    return df


# TODO I don't get this param
def get_consensus_matrix(self, quant="chrom_area"):
    """
    Get a matrix of consensus features with samples as columns and consensus features as rows.
    """
    if quant not in self.features_df.columns:
        self.logger.error(
            f"Quantification method {quant} not found in features_df.",
        )
        return None

    # Use Polars join instead of pandas merge
    features_subset = self.features_df.select(["feature_uid", "sample_uid", quant])
    consensus_mapping_subset = self.consensus_mapping_df.select([
        "consensus_uid",
        "feature_uid",
    ])

    df1 = features_subset.join(
        consensus_mapping_subset,
        on="feature_uid",
        how="left",
    )

    # Convert to pandas for pivot operation (Polars pivot is still evolving)
    df1_pd = df1.to_pandas()
    df2 = df1_pd.pivot_table(
        index="consensus_uid",
        columns="sample_uid",
        values=quant,
        aggfunc="max",
    )

    # Create sample_uid to sample_name mapping using Polars
    sample_mapping = dict(
        self.samples_df.select(["sample_uid", "sample_name"]).iter_rows(),
    )
    # replace sample_uid with sample_name in df2
    df2 = df2.rename(columns=sample_mapping)

    # round to integer
    df2 = df2.round()
    # set consensus_id as uint64
    df2.index = df2.index.astype("uint64")
    # set index to consensus_id
    df2.index.name = "consensus_uid"
    return df2


def get_gaps_matrix(self, uids=None):
    """
    Get a matrix of gaps between consensus features with samples as columns and consensus features as rows.
    """
    if self.consensus_df is None:
        self.logger.error("No consensus map found.")
        return None
    uids = self._get_consensus_uids(uids)

    df1 = self.get_consensus_matrix(quant="filled")
    if df1 is None or df1.empty:
        self.logger.warning("No gap data found.")
        return None
    # keep only rows where consensus_id is in ids - use pandas indexing since df1 is already pandas
    df1 = df1[df1.index.isin(uids)]
    return df1


def get_gaps_stats(self, uids=None):
    """
    Get statistics about gaps in the consensus features.
    """

    df = self.get_gaps_matrix(uids=uids)

    # For each column, count how many times the value is True, False, or None. Summarize in a new df with three rows: True, False, None.
    if df is None or df.empty:
        self.logger.warning("No gap data found.")
        return None
    gaps_stats = pd.DataFrame(
        {
            "aligned": df.apply(lambda x: (~x.astype(bool)).sum()),
            "filled": df.apply(lambda x: x.astype(bool).sum() - pd.isnull(x).sum()),
            "missing": df.apply(lambda x: pd.isnull(x).sum()),
        },
    )
    return gaps_stats


# TODO is uid not supposed to be a list anymore?
def get_consensus_matches(self, uids=None):
    uids = self._get_consensus_uids(uids)

    # find all rows in consensus_mapping_df with consensus_id=id - use Polars filtering
    fid = (
        self.consensus_mapping_df.filter(
            pl.col("consensus_uid").is_in(uids),
        )
        .select("feature_uid")
        .to_series()
        .to_list()
    )
    # select all rows in features_df with uid in fid
    matches = self.features_df.filter(pl.col("feature_uid").is_in(fid)).clone()
    return matches


def fill_reset(self):
    # remove all features with filled=True
    if self.features_df is None:
        self.logger.warning("No features found.")
        return
    l1 = len(self.features_df)
    self.features_df = self.features_df.filter(~pl.col("filled"))
    # remove all rows in consensus_mapping_df where feature_uid is not in features_df['uid']

    feature_uids_to_keep = self.features_df["feature_uid"].to_list()
    self.consensus_mapping_df = self.consensus_mapping_df.filter(
        pl.col("feature_uid").is_in(feature_uids_to_keep),
    )
    self.logger.info(
        f"Reset filled chromatograms. Chroms removed: {l1 - len(self.features_df)}",
    )


def _get_feature_uids(self, uids=None, seed=42):
    """
    Helper function to get feature_uids from features_df based on input uids.
    If uids is None, returns all feature_uids.
    If uids is a single integer, returns a random sample of feature_uids.
    If uids is a list of strings, returns feature_uids corresponding to those feature_uids.
    If uids is a list of integers, returns feature_uids corresponding to those feature_uids.
    """
    if uids is None:
        # get all feature_uids from features_df
        return self.features_df["feature_uid"].to_list()
    elif isinstance(uids, int):
        # choose a random sample of feature_uids
        if len(self.features_df) > uids:
            np.random.seed(seed)
            return np.random.choice(
                self.features_df["feature_uid"].to_list(),
                uids,
                replace=False,
            ).tolist()
        else:
            return self.features_df["feature_uid"].to_list()
    else:
        # iterate over all uids. If the item is a string, assume it's a feature_uid
        feature_uids = []
        for uid in uids:
            if isinstance(uid, str):
                matching_rows = self.features_df.filter(pl.col("feature_uid") == uid)
                if not matching_rows.is_empty():
                    feature_uids.append(
                        matching_rows.row(0, named=True)["feature_uid"],
                    )
            elif isinstance(uid, int):
                if uid in self.features_df["feature_uid"].to_list():
                    feature_uids.append(uid)
        # remove duplicates
        feature_uids = list(set(feature_uids))
        return feature_uids


def _get_consensus_uids(self, uids=None, seed=42):
    """
    Helper function to get consensus_uids from consensus_df based on input uids.
    If uids is None, returns all consensus_uids.
    If uids is a single integer, returns a random sample of consensus_uids.
    If uids is a list of strings, returns consensus_uids corresponding to those consensus_ids.
    If uids is a list of integers, returns consensus_uids corresponding to those consensus_uids.
    """
    # Check if consensus_df is empty or doesn't have required columns
    if self.consensus_df.is_empty() or "consensus_uid" not in self.consensus_df.columns:
        return []

    if uids is None:
        # get all consensus_uids from consensus_df
        return self.consensus_df["consensus_uid"].to_list()
    elif isinstance(uids, int):
        # choose a random sample of consensus_uids
        if len(self.consensus_df) > uids:
            np.random.seed(seed)  # for reproducibility
            return np.random.choice(
                self.consensus_df["consensus_uid"].to_list(),
                uids,
                replace=False,
            ).tolist()
        else:
            return self.consensus_df["consensus_uid"].to_list()
    else:
        # iterate over all uids. If the item is a string, assume it's a consensus_id
        consensus_uids = []
        for uid in uids:
            if isinstance(uid, str):
                matching_rows = self.consensus_df.filter(pl.col("consensus_id") == uid)
                if not matching_rows.is_empty():
                    consensus_uids.append(
                        matching_rows.row(0, named=True)["consensus_uid"],
                    )
            elif isinstance(uid, int):
                if uid in self.consensus_df["consensus_uid"].to_list():
                    consensus_uids.append(uid)
        # remove duplicates
        consensus_uids = list(set(consensus_uids))
        return consensus_uids


def _get_sample_uids(self, samples=None, seed=42):
    """
    Helper function to get sample_uids from samples_df based on input samples.
    If samples is None, returns all sample_uids.
    If samples is a single integer, returns a random sample of sample_uids.
    If samples is a list of strings, returns sample_uids corresponding to those sample_names.
    If samples is a list of integers, returns sample_uids corresponding to those sample_uids.
    """
    if samples is None:
        # get all sample_uids from samples_df
        return self.samples_df["sample_uid"].to_list()
    elif isinstance(samples, int):
        # choose a random sample of sample_uids
        if len(self.samples_df) > samples:
            np.random.seed(seed)  # for reproducibility
            return np.random.choice(
                self.samples_df["sample_uid"].to_list(),
                samples,
                replace=False,
            ).tolist()
        else:
            return self.samples_df["sample_uid"].to_list()
    else:
        # iterate over all samples. If the item is a string, assume it's a sample_name
        sample_uids = []
        for sample in samples:
            if isinstance(sample, str):
                matching_rows = self.samples_df.filter(pl.col("sample_name") == sample)
                if not matching_rows.is_empty():
                    sample_uids.append(
                        matching_rows.row(0, named=True)["sample_uid"],
                    )
            elif isinstance(sample, int):
                if sample in self.samples_df["sample_uid"].to_list():
                    sample_uids.append(sample)
        # remove duplicates
        sample_uids = list(set(sample_uids))
        return sample_uids


def get_orphans(self):
    """
    Get all features that are not in the consensus mapping.
    """
    not_in_consensus = self.features_df.filter(
        ~self.features_df["feature_uid"].is_in(self.consensus_mapping_df["feature_uid"].to_list())
    )
    return not_in_consensus


def compress(self, features=True, ms2=True, chrom=False, ms2_max=5):
    """
    Perform compress_features, compress_ms2, and compress_chrom operations.

    Parameters:
        max_replicates (int): Maximum number of MS2 replicates to keep per consensus_uid and energy combination
    """
    self.logger.info("Starting full compression...")
    if features:
        self.compress_features()
    if ms2:
        self.compress_ms2(max_replicates=ms2_max)
    if chrom:
        self.compress_chrom()
    self.logger.info("Compression completed")


def compress_features(self):
    """
    Compress features_df by:
    1. Deleting features that are not associated to any consensus (according to consensus_mapping_df)
    2. Setting the m2_specs column to None to save memory
    """
    if self.features_df is None or self.features_df.is_empty():
        self.logger.warning("No features_df found.")
        return

    if self.consensus_mapping_df is None or self.consensus_mapping_df.is_empty():
        self.logger.warning("No consensus_mapping_df found.")
        return

    initial_count = len(self.features_df)

    # Get feature_uids that are associated with consensus features
    consensus_feature_uids = self.consensus_mapping_df["feature_uid"].to_list()

    # Filter features_df to keep only features associated with consensus
    self.features_df = self.features_df.filter(
        pl.col("feature_uid").is_in(consensus_feature_uids),
    )

    # Set ms2_specs column to None if it exists
    if "ms2_specs" in self.features_df.columns:
        # Create a list of None values with the same length as the dataframe
        # This preserves the Object dtype instead of converting to Null
        none_values = [None] * len(self.features_df)
        self.features_df = self.features_df.with_columns(
            pl.Series("ms2_specs", none_values, dtype=pl.Object),
        )

    removed_count = initial_count - len(self.features_df)
    self.logger.info(
        f"Compressed features: removed {removed_count} features not in consensus, cleared ms2_specs column"
    )


def restore_features(self, samples=None, maps=False):
    """
    Update specific columns (chrom, chrom_area, ms2_scans, ms2_specs) in features_df
    from the corresponding samples by reading features_df from the sample5 file.
    Use the feature_id for matching.

    Parameters:
        samples (list, optional): List of sample_uids or sample_names to restore.
                                 If None, restores all samples.
        maps (bool, optional): If True, also load featureXML data and update study.feature_maps.
    """
    import datetime
    from masster.sample.sample import Sample

    if self.features_df is None or self.features_df.is_empty():
        self.logger.error("No features_df found in study.")
        return

    if self.samples_df is None or self.samples_df.is_empty():
        self.logger.error("No samples_df found in study.")
        return

    # Get sample_uids to process
    sample_uids = self._get_sample_uids(samples)

    if not sample_uids:
        self.logger.warning("No valid samples specified.")
        return

    # Columns to update from sample data
    columns_to_update = ["chrom", "chrom_area", "ms2_scans", "ms2_specs"]

    self.logger.info(f"Restoring columns {columns_to_update} from {len(sample_uids)} samples...")

    # Create a mapping of (sample_uid, feature_id) to feature_uid from study.features_df
    study_feature_mapping = {}
    for row in self.features_df.iter_rows(named=True):
        if "feature_id" in row and "feature_uid" in row and "sample_uid" in row:
            key = (row["sample_uid"], row["feature_id"])
            study_feature_mapping[key] = row["feature_uid"]

    # Process each sample
    tqdm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]
    for sample_uid in tqdm(
        sample_uids,
        unit="sample",
        disable=tqdm_disable,
        desc=f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Restoring samples",
    ):
        # Get sample info
        sample_row = self.samples_df.filter(pl.col("sample_uid") == sample_uid)
        if sample_row.is_empty():
            self.logger.warning(f"Sample with uid {sample_uid} not found in samples_df.")
            continue

        sample_info = sample_row.row(0, named=True)
        sample_path = sample_info.get("sample_path")
        sample_name = sample_info.get("sample_name")

        if not sample_path or not os.path.exists(sample_path):
            self.logger.warning(f"Sample file not found for {sample_name}: {sample_path}")
            continue

        try:
            # Load sample to get its features_df
            # Use a direct load call with map=False to prevent feature synchronization
            # which would remove filled features that don't exist in the original FeatureMap
            sample = Sample(log_level="DEBUG")
            sample._load_sample5(sample_path, map=False)

            if sample.features_df is None or sample.features_df.is_empty():
                self.logger.warning(f"No features found in sample {sample_name}")
                continue

            # Create update data for this sample
            updates_made = 0
            for row in sample.features_df.iter_rows(named=True):
                feature_id = row.get("feature_id")
                if feature_id is None:
                    continue

                key = (sample_uid, feature_id)
                if key in study_feature_mapping:
                    feature_uid = study_feature_mapping[key]

                    # Update the specific columns in study.features_df
                    for col in columns_to_update:
                        if col in row and col in self.features_df.columns:
                            # Get the original column dtype to preserve it
                            original_dtype = self.features_df[col].dtype

                            # Update the specific row and column, preserving dtype
                            mask = (pl.col("feature_uid") == feature_uid) & (pl.col("sample_uid") == sample_uid)

                            # Handle object columns (like Chromatogram) differently
                            if original_dtype == pl.Object:
                                self.features_df = self.features_df.with_columns(
                                    pl.when(mask)
                                    .then(pl.lit(row[col], dtype=original_dtype, allow_object=True))
                                    .otherwise(pl.col(col))
                                    .alias(col),
                                )
                            else:
                                self.features_df = self.features_df.with_columns(
                                    pl.when(mask)
                                    .then(pl.lit(row[col], dtype=original_dtype))
                                    .otherwise(pl.col(col))
                                    .alias(col),
                                )
                    updates_made += 1

            self.logger.debug(f"Updated {updates_made} features from sample {sample_name}")

            # If maps is True, load featureXML data
            if maps:
                if hasattr(sample, "feature_maps"):
                    self.feature_maps.extend(sample.feature_maps)

        except Exception as e:
            self.logger.error(f"Failed to load sample {sample_name}: {e}")
            continue

    self.logger.info(f"Completed restoring columns {columns_to_update} from {len(sample_uids)} samples")


def restore_chrom(self, samples=None, mz_tol=0.010, rt_tol=10.0):
    """
    Restore chromatograms from individual .sample5 files and gap-fill missing ones.

    This function combines the functionality of restore_features() and fill_chrom():
    1. First restores chromatograms from individual .sample5 files (like restore_features)
    2. Then gap-fills any remaining empty chromatograms (like fill_chrom)
    3. ONLY updates the 'chrom' column, not chrom_area or other derived values

    Parameters:
        samples (list, optional): List of sample_uids or sample_names to process.
                                 If None, processes all samples.
        mz_tol (float): m/z tolerance for gap filling (default: 0.010)
        rt_tol (float): RT tolerance for gap filling (default: 10.0)
    """
    import datetime
    import numpy as np
    from masster.sample.sample import Sample
    from masster.chromatogram import Chromatogram

    if self.features_df is None or self.features_df.is_empty():
        self.logger.error("No features_df found in study.")
        return

    if self.samples_df is None or self.samples_df.is_empty():
        self.logger.error("No samples_df found in study.")
        return

    # Get sample_uids to process
    sample_uids = self._get_sample_uids(samples)
    if not sample_uids:
        self.logger.warning("No valid samples specified.")
        return

    self.logger.info(f"Restoring chromatograms from {len(sample_uids)} samples...")

    # Create mapping of (sample_uid, feature_id) to feature_uid
    study_feature_mapping = {}
    for row in self.features_df.iter_rows(named=True):
        if "feature_id" in row and "feature_uid" in row and "sample_uid" in row:
            key = (row["sample_uid"], row["feature_id"])
            study_feature_mapping[key] = row["feature_uid"]

    # Phase 1: Restore from individual .sample5 files (like restore_features)
    restored_count = 0
    tqdm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]

    self.logger.info("Phase 1: Restoring chromatograms from .sample5 files...")
    for sample_uid in tqdm(
        sample_uids,
        desc=f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Restoring from samples",
        disable=tqdm_disable,
    ):
        # Get sample info
        sample_row = self.samples_df.filter(pl.col("sample_uid") == sample_uid)
        if sample_row.is_empty():
            self.logger.warning(f"Sample with uid {sample_uid} not found.")
            continue

        sample_info = sample_row.row(0, named=True)
        sample_path = sample_info.get("sample_path")
        sample_name = sample_info.get("sample_name")

        if not sample_path or not os.path.exists(sample_path):
            self.logger.warning(f"Sample file not found: {sample_path}")
            continue

        try:
            # Load sample (with map=False to prevent feature synchronization)
            sample = Sample(log_level="WARNING")
            sample._load_sample5(sample_path, map=False)

            if sample.features_df is None or sample.features_df.is_empty():
                self.logger.warning(f"No features found in sample {sample_name}")
                continue

            # Update chromatograms from this sample
            for row in sample.features_df.iter_rows(named=True):
                feature_id = row.get("feature_id")
                chrom = row.get("chrom")

                if feature_id is None or chrom is None:
                    continue

                key = (sample_uid, feature_id)
                if key in study_feature_mapping:
                    feature_uid = study_feature_mapping[key]

                    # Update only the chrom column
                    mask = (pl.col("feature_uid") == feature_uid) & (pl.col("sample_uid") == sample_uid)
                    self.features_df = self.features_df.with_columns(
                        pl.when(mask)
                        .then(pl.lit(chrom, dtype=pl.Object, allow_object=True))
                        .otherwise(pl.col("chrom"))
                        .alias("chrom"),
                    )
                    restored_count += 1

        except Exception as e:
            self.logger.error(f"Failed to load sample {sample_name}: {e}")
            continue

    self.logger.info(f"Phase 1 complete: Restored {restored_count} chromatograms from .sample5 files")

    # Phase 2: Gap-fill remaining empty chromatograms (like fill_chrom)
    self.logger.info("Phase 2: Gap-filling remaining empty chromatograms...")

    # Count how many chromatograms are still missing
    empty_chroms = self.features_df.filter(pl.col("chrom").is_null()).height
    total_chroms = len(self.features_df)

    self.logger.debug(
        f"Chromatograms still missing: {empty_chroms}/{total_chroms} ({empty_chroms / total_chroms * 100:.1f}%)"
    )

    if empty_chroms == 0:
        self.logger.info("All chromatograms restored from .sample5 files. No gap-filling needed.")
        return

    # Get consensus info for gap filling
    consensus_info = {}
    for row in self.consensus_df.iter_rows(named=True):
        consensus_info[row["consensus_uid"]] = {
            "rt_start_mean": row["rt_start_mean"],
            "rt_end_mean": row["rt_end_mean"],
            "mz": row["mz"],
            "rt": row["rt"],
        }

    filled_count = 0

    # Process each sample that has missing chromatograms
    for sample_uid in tqdm(
        sample_uids,
        desc=f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Gap-filling missing chromatograms",
        disable=tqdm_disable,
    ):
        # Get features with missing chromatograms for this sample
        missing_features = self.features_df.filter(
            (pl.col("sample_uid") == sample_uid) & (pl.col("chrom").is_null()),
        )

        if missing_features.is_empty():
            continue

        # Get sample info
        sample_row = self.samples_df.filter(pl.col("sample_uid") == sample_uid)
        sample_info = sample_row.row(0, named=True)
        sample_path = sample_info.get("sample_path")
        sample_name = sample_info.get("sample_name")

        if not sample_path or not os.path.exists(sample_path):
            continue

        try:
            # Load sample for MS1 data extraction
            sample = Sample(log_level="WARNING")
            sample._load_sample5(sample_path, map=False)

            if not hasattr(sample, "ms1_df") or sample.ms1_df is None or sample.ms1_df.is_empty():
                continue

            # Process each missing feature
            for feature_row in missing_features.iter_rows(named=True):
                feature_uid = feature_row["feature_uid"]
                mz = feature_row["mz"]
                rt = feature_row["rt"]
                rt_start = feature_row.get("rt_start", rt - rt_tol)
                rt_end = feature_row.get("rt_end", rt + rt_tol)

                # Extract EIC from MS1 data
                d = sample.ms1_df.filter(
                    (pl.col("mz") >= mz - mz_tol)
                    & (pl.col("mz") <= mz + mz_tol)
                    & (pl.col("rt") >= rt_start - rt_tol)
                    & (pl.col("rt") <= rt_end + rt_tol),
                )

                # Create chromatogram
                if d.is_empty():
                    # Create empty chromatogram
                    eic = Chromatogram(
                        rt=np.array([rt_start, rt_end]),
                        inty=np.array([0.0, 0.0]),
                        label=f"EIC mz={mz:.4f} (gap-filled)",
                        file=sample_path,
                        mz=mz,
                        mz_tol=mz_tol,
                        feature_start=rt_start,
                        feature_end=rt_end,
                        feature_apex=rt,
                    )
                else:
                    # Create real chromatogram from data
                    eic_rt = d.group_by("rt").agg(pl.col("inty").max()).sort("rt")

                    if len(eic_rt) > 4:
                        eic = Chromatogram(
                            eic_rt["rt"].to_numpy(),
                            eic_rt["inty"].to_numpy(),
                            label=f"EIC mz={mz:.4f} (gap-filled)",
                            file=sample_path,
                            mz=mz,
                            mz_tol=mz_tol,
                            feature_start=rt_start,
                            feature_end=rt_end,
                            feature_apex=rt,
                        ).find_peaks()
                    else:
                        eic = Chromatogram(
                            eic_rt["rt"].to_numpy(),
                            eic_rt["inty"].to_numpy(),
                            label=f"EIC mz={mz:.4f} (gap-filled)",
                            file=sample_path,
                            mz=mz,
                            mz_tol=mz_tol,
                            feature_start=rt_start,
                            feature_end=rt_end,
                            feature_apex=rt,
                        )

                # Update the chromatogram in the study
                mask = pl.col("feature_uid") == feature_uid
                self.features_df = self.features_df.with_columns(
                    pl.when(mask)
                    .then(pl.lit(eic, dtype=pl.Object, allow_object=True))
                    .otherwise(pl.col("chrom"))
                    .alias("chrom"),
                )
                filled_count += 1

        except Exception as e:
            self.logger.error(f"Failed to gap-fill sample {sample_name}: {e}")
            continue

    self.logger.info(f"Phase 2 complete: Gap-filled {filled_count} chromatograms")

    # Final summary
    final_non_null = self.features_df.filter(pl.col("chrom").is_not_null()).height
    final_total = len(self.features_df)

    self.logger.info(
        f"Chromatogram restoration complete: {final_non_null}/{final_total} ({final_non_null / final_total * 100:.1f}%)"
    )
    self.logger.info(f"Restored from .sample5 files: {restored_count}, Gap-filled from raw data: {filled_count}")


def compress_ms2(self, max_replicates=5):
    """
    Reduce the number of entries matching any pair of (consensus and energy) to max XY rows.
    Groups all rows by consensus_uid and energy. For each group, sort by number_frags * prec_inty,
    and then pick the top XY rows. Discard the others.

    Parameters:
        max_replicates (int): Maximum number of replicates to keep per consensus_uid and energy combination
    """
    if self.consensus_ms2 is None or self.consensus_ms2.is_empty():
        self.logger.warning("No consensus_ms2 found.")
        return

    initial_count = len(self.consensus_ms2)

    # Create a ranking score based on number_frags * prec_inty
    # Handle None values by treating them as 0
    self.consensus_ms2 = self.consensus_ms2.with_columns([
        (pl.col("number_frags").fill_null(0) * pl.col("prec_inty").fill_null(0)).alias("ranking_score"),
    ])

    # Group by consensus_uid and energy, then rank by score and keep top max_replicates
    compressed_ms2 = (
        self.consensus_ms2.with_row_count("row_id")  # Add row numbers for stable sorting
        .sort(["consensus_uid", "energy", "ranking_score", "row_id"], descending=[False, False, True, False])
        .with_columns([
            pl.int_range(pl.len()).over(["consensus_uid", "energy"]).alias("rank"),
        ])
        .filter(pl.col("rank") < max_replicates)
        .drop(["ranking_score", "row_id", "rank"])
    )

    self.consensus_ms2 = compressed_ms2

    removed_count = initial_count - len(self.consensus_ms2)
    self.logger.info(
        f"Compressed MS2 data: removed {removed_count} entries, kept max {max_replicates} per consensus/energy pair"
    )


def compress_chrom(self):
    """
    Set the chrom column in study.features_df to null to save memory.

    This function clears all chromatogram objects from the features_df, which can
    significantly reduce memory usage in large studies.
    """
    if self.features_df is None or self.features_df.is_empty():
        self.logger.warning("No features_df found.")
        return

    if "chrom" not in self.features_df.columns:
        self.logger.warning("No 'chrom' column found in features_df.")
        return

    # Count non-null chromatograms before compression
    non_null_count = self.features_df.filter(pl.col("chrom").is_not_null()).height

    # Set chrom column to None while keeping dtype as object
    self.features_df = self.features_df.with_columns(
        pl.lit(None, dtype=pl.Object).alias("chrom"),
    )

    self.logger.info(f"Compressed chromatograms: cleared {non_null_count} chromatogram objects from features_df")


def set_source(self, filename):
    """
    Reassign file_source for all samples in samples_df. If filename contains only a path,
    keep the current basename and build an absolute path. Check that the new file exists
    before overwriting the old file_source.

    Parameters:
        filename (str): New file path or directory path for all samples

    Returns:
        None
    """
    import os

    if self.samples_df is None or len(self.samples_df) == 0:
        self.logger.warning("No samples found in study.")
        return

    updated_count = 0
    failed_count = 0

    # Get all current file_source values
    current_sources = self.samples_df.get_column("file_source").to_list()
    sample_names = self.samples_df.get_column("sample_name").to_list()

    new_sources = []

    for i, (current_source, sample_name) in enumerate(zip(current_sources, sample_names)):
        # Check if filename is just a directory path
        if os.path.isdir(filename):
            if current_source is None or current_source == "":
                self.logger.warning(f"Cannot build path for sample '{sample_name}': no current file_source available")
                new_sources.append(current_source)
                failed_count += 1
                continue

            # Get the basename from current file_source
            current_basename = os.path.basename(current_source)
            # Build new absolute path
            new_file_path = os.path.join(filename, current_basename)
        else:
            # filename is a full path, make it absolute
            new_file_path = os.path.abspath(filename)

        # Check if the new file exists
        if not os.path.exists(new_file_path):
            self.logger.warning(f"File does not exist for sample '{sample_name}': {new_file_path}")
            new_sources.append(current_source)
            failed_count += 1
            continue

        # File exists, update source
        new_sources.append(new_file_path)
        updated_count += 1

        # Log individual updates at debug level
        self.logger.debug(f"Updated file_source for sample '{sample_name}': {current_source} -> {new_file_path}")

    # Update the samples_df with new file_source values
    self.samples_df = self.samples_df.with_columns(
        pl.Series("file_source", new_sources).alias("file_source"),
    )

    # Log summary
    if updated_count > 0:
        self.logger.info(f"Updated file_source for {updated_count} samples")
    if failed_count > 0:
        self.logger.warning(f"Failed to update file_source for {failed_count} samples")


def features_select(
    self,
    mz=None,
    rt=None,
    inty=None,
    sample_uid=None,
    sample_name=None,
    consensus_uid=None,
    feature_uid=None,
    filled=None,
    quality=None,
    chrom_coherence=None,
    chrom_prominence=None,
    chrom_prominence_scaled=None,
    chrom_height_scaled=None,
):
    """
    Select features from features_df based on specified criteria and return the filtered DataFrame.

    OPTIMIZED VERSION: Combines all filters into a single operation for better performance.

    Parameters:
        mz: m/z range filter (tuple for range, single value for minimum)
        rt: retention time range filter (tuple for range, single value for minimum)
        inty: intensity filter (tuple for range, single value for minimum)
        sample_uid: sample UID filter (list, single value, or tuple for range)
        sample_name: sample name filter (list or single value)
        consensus_uid: consensus UID filter (list, single value, or tuple for range)
        feature_uid: feature UID filter (list, single value, or tuple for range)
        filled: filter for filled/not filled features (bool)
        quality: quality score filter (tuple for range, single value for minimum)
        chrom_coherence: chromatogram coherence filter (tuple for range, single value for minimum)
        chrom_prominence: chromatogram prominence filter (tuple for range, single value for minimum)
        chrom_prominence_scaled: scaled chromatogram prominence filter (tuple for range, single value for minimum)
        chrom_height_scaled: scaled chromatogram height filter (tuple for range, single value for minimum)

    Returns:
        polars.DataFrame: Filtered features DataFrame
    """
    if self.features_df is None or self.features_df.is_empty():
        self.logger.warning("No features found in study.")
        return pl.DataFrame()

    # Early return if no filters provided - performance optimization
    filter_params = [
        mz,
        rt,
        inty,
        sample_uid,
        sample_name,
        consensus_uid,
        feature_uid,
        filled,
        quality,
        chrom_coherence,
        chrom_prominence,
        chrom_prominence_scaled,
        chrom_height_scaled,
    ]
    if all(param is None for param in filter_params):
        return self.features_df.clone()

    initial_count = len(self.features_df)

    # Pre-check available columns once for efficiency
    available_columns = set(self.features_df.columns)

    # Build all filter conditions first, then apply them all at once
    filter_conditions = []
    warnings = []

    # Filter by m/z
    if mz is not None:
        if isinstance(mz, tuple) and len(mz) == 2:
            min_mz, max_mz = mz
            filter_conditions.append((pl.col("mz") >= min_mz) & (pl.col("mz") <= max_mz))
        else:
            filter_conditions.append(pl.col("mz") >= mz)

    # Filter by retention time
    if rt is not None:
        if isinstance(rt, tuple) and len(rt) == 2:
            min_rt, max_rt = rt
            filter_conditions.append((pl.col("rt") >= min_rt) & (pl.col("rt") <= max_rt))
        else:
            filter_conditions.append(pl.col("rt") >= rt)

    # Filter by intensity
    if inty is not None:
        if isinstance(inty, tuple) and len(inty) == 2:
            min_inty, max_inty = inty
            filter_conditions.append((pl.col("inty") >= min_inty) & (pl.col("inty") <= max_inty))
        else:
            filter_conditions.append(pl.col("inty") >= inty)

    # Filter by sample_uid
    if sample_uid is not None:
        if isinstance(sample_uid, (list, tuple)):
            if len(sample_uid) == 2 and not isinstance(sample_uid, list):
                # Treat as range
                min_uid, max_uid = sample_uid
                filter_conditions.append((pl.col("sample_uid") >= min_uid) & (pl.col("sample_uid") <= max_uid))
            else:
                # Treat as list
                filter_conditions.append(pl.col("sample_uid").is_in(sample_uid))
        else:
            filter_conditions.append(pl.col("sample_uid") == sample_uid)

    # Filter by sample_name (requires pre-processing)
    if sample_name is not None:
        # Get sample_uids for the given sample names
        if isinstance(sample_name, list):
            sample_uids_for_names = self.samples_df.filter(
                pl.col("sample_name").is_in(sample_name),
            )["sample_uid"].to_list()
        else:
            sample_uids_for_names = self.samples_df.filter(
                pl.col("sample_name") == sample_name,
            )["sample_uid"].to_list()

        if sample_uids_for_names:
            filter_conditions.append(pl.col("sample_uid").is_in(sample_uids_for_names))
        else:
            filter_conditions.append(pl.lit(False))  # No matching samples

    # Filter by consensus_uid
    if consensus_uid is not None:
        if isinstance(consensus_uid, (list, tuple)):
            if len(consensus_uid) == 2 and not isinstance(consensus_uid, list):
                # Treat as range
                min_uid, max_uid = consensus_uid
                filter_conditions.append((pl.col("consensus_uid") >= min_uid) & (pl.col("consensus_uid") <= max_uid))
            else:
                # Treat as list
                filter_conditions.append(pl.col("consensus_uid").is_in(consensus_uid))
        else:
            filter_conditions.append(pl.col("consensus_uid") == consensus_uid)

    # Filter by feature_uid
    if feature_uid is not None:
        if isinstance(feature_uid, (list, tuple)):
            if len(feature_uid) == 2 and not isinstance(feature_uid, list):
                # Treat as range
                min_uid, max_uid = feature_uid
                filter_conditions.append((pl.col("feature_uid") >= min_uid) & (pl.col("feature_uid") <= max_uid))
            else:
                # Treat as list
                filter_conditions.append(pl.col("feature_uid").is_in(feature_uid))
        else:
            filter_conditions.append(pl.col("feature_uid") == feature_uid)

    # Filter by filled status
    if filled is not None:
        if "filled" in available_columns:
            if filled:
                filter_conditions.append(pl.col("filled"))
            else:
                filter_conditions.append(~pl.col("filled") | pl.col("filled").is_null())
        else:
            warnings.append("'filled' column not found in features_df")

    # Filter by quality
    if quality is not None:
        if "quality" in available_columns:
            if isinstance(quality, tuple) and len(quality) == 2:
                min_quality, max_quality = quality
                filter_conditions.append((pl.col("quality") >= min_quality) & (pl.col("quality") <= max_quality))
            else:
                filter_conditions.append(pl.col("quality") >= quality)
        else:
            warnings.append("'quality' column not found in features_df")

    # Filter by chromatogram coherence
    if chrom_coherence is not None:
        if "chrom_coherence" in available_columns:
            if isinstance(chrom_coherence, tuple) and len(chrom_coherence) == 2:
                min_coherence, max_coherence = chrom_coherence
                filter_conditions.append(
                    (pl.col("chrom_coherence") >= min_coherence) & (pl.col("chrom_coherence") <= max_coherence)
                )
            else:
                filter_conditions.append(pl.col("chrom_coherence") >= chrom_coherence)
        else:
            warnings.append("'chrom_coherence' column not found in features_df")

    # Filter by chromatogram prominence
    if chrom_prominence is not None:
        if "chrom_prominence" in available_columns:
            if isinstance(chrom_prominence, tuple) and len(chrom_prominence) == 2:
                min_prominence, max_prominence = chrom_prominence
                filter_conditions.append(
                    (pl.col("chrom_prominence") >= min_prominence) & (pl.col("chrom_prominence") <= max_prominence)
                )
            else:
                filter_conditions.append(pl.col("chrom_prominence") >= chrom_prominence)
        else:
            warnings.append("'chrom_prominence' column not found in features_df")

    # Filter by scaled chromatogram prominence
    if chrom_prominence_scaled is not None:
        if "chrom_prominence_scaled" in available_columns:
            if isinstance(chrom_prominence_scaled, tuple) and len(chrom_prominence_scaled) == 2:
                min_prominence_scaled, max_prominence_scaled = chrom_prominence_scaled
                filter_conditions.append(
                    (pl.col("chrom_prominence_scaled") >= min_prominence_scaled)
                    & (pl.col("chrom_prominence_scaled") <= max_prominence_scaled)
                )
            else:
                filter_conditions.append(pl.col("chrom_prominence_scaled") >= chrom_prominence_scaled)
        else:
            warnings.append("'chrom_prominence_scaled' column not found in features_df")

    # Filter by scaled chromatogram height
    if chrom_height_scaled is not None:
        if "chrom_height_scaled" in available_columns:
            if isinstance(chrom_height_scaled, tuple) and len(chrom_height_scaled) == 2:
                min_height_scaled, max_height_scaled = chrom_height_scaled
                filter_conditions.append(
                    (pl.col("chrom_height_scaled") >= min_height_scaled)
                    & (pl.col("chrom_height_scaled") <= max_height_scaled)
                )
            else:
                filter_conditions.append(pl.col("chrom_height_scaled") >= chrom_height_scaled)
        else:
            warnings.append("'chrom_height_scaled' column not found in features_df")

    # Log all warnings once at the end for efficiency
    for warning in warnings:
        self.logger.warning(warning)

    # Apply all filters at once using lazy evaluation for optimal performance
    if filter_conditions:
        # Combine all conditions with AND
        combined_filter = filter_conditions[0]
        for condition in filter_conditions[1:]:
            combined_filter = combined_filter & condition

        # Apply the combined filter using lazy evaluation
        feats = self.features_df.lazy().filter(combined_filter).collect()
    else:
        feats = self.features_df.clone()

    final_count = len(feats)

    if final_count == 0:
        self.logger.warning("No features remaining after applying selection criteria.")
    else:
        # removed_count = initial_count - final_count
        self.logger.info(f"Features selected: {final_count} (out of {initial_count})")

    return feats


def features_filter(self, features):
    """
    Filter features_df by keeping only features that match the given criteria.
    This keeps only the specified features and removes all others.

    OPTIMIZED VERSION: Batch operations and reduced overhead for better performance.

    Parameters:
        features: Features to keep. Can be:
                 - polars.DataFrame: Features DataFrame (will use feature_uid column)
                 - list: List of feature_uids to keep
                 - int: Single feature_uid to keep

    Returns:
        None (modifies self.features_df in place)
    """
    if self.features_df is None or self.features_df.is_empty():
        self.logger.warning("No features found in study.")
        return

    # Early return if no features provided
    if features is None:
        self.logger.warning("No features provided for filtering.")
        return

    initial_count = len(self.features_df)

    # Determine feature_uids to keep - optimized type checking
    if isinstance(features, pl.DataFrame):
        if "feature_uid" not in features.columns:
            self.logger.error("features DataFrame must contain 'feature_uid' column")
            return
        feature_uids_to_keep = features["feature_uid"].to_list()
    elif isinstance(features, (list, tuple)):
        feature_uids_to_keep = list(features)  # Convert tuple to list if needed
    elif isinstance(features, int):
        feature_uids_to_keep = [features]
    else:
        self.logger.error("features parameter must be a DataFrame, list, tuple, or int")
        return

    # Early return if no UIDs to keep
    if not feature_uids_to_keep:
        self.logger.warning("No feature UIDs provided for filtering.")
        return

    # Convert to set for faster lookup if list is large
    if len(feature_uids_to_keep) > 100:
        feature_uids_set = set(feature_uids_to_keep)
        # Use the set for filtering if it's significantly smaller
        if len(feature_uids_set) < len(feature_uids_to_keep) * 0.8:
            feature_uids_to_keep = list(feature_uids_set)

    # Create filter condition once - keep only the specified features
    filter_condition = pl.col("feature_uid").is_in(feature_uids_to_keep)

    # Apply filter to features_df using lazy evaluation for better performance
    self.features_df = self.features_df.lazy().filter(filter_condition).collect()

    # Apply filter to consensus_mapping_df if it exists - batch operation
    mapping_removed_count = 0
    if self.consensus_mapping_df is not None and not self.consensus_mapping_df.is_empty():
        initial_mapping_count = len(self.consensus_mapping_df)
        self.consensus_mapping_df = self.consensus_mapping_df.lazy().filter(filter_condition).collect()
        mapping_removed_count = initial_mapping_count - len(self.consensus_mapping_df)

    # Calculate results once and log efficiently
    final_count = len(self.features_df)
    removed_count = initial_count - final_count

    # Single comprehensive log message
    if mapping_removed_count > 0:
        self.logger.info(
            f"Kept {final_count} features and removed {mapping_removed_count} consensus mappings. Filtered out {removed_count} features."
        )
    else:
        self.logger.info(f"Kept {final_count} features. Filtered out {removed_count} features.")


def features_delete(self, features):
    """
    Delete features from features_df based on feature identifiers.
    This removes the specified features and keeps all others (opposite of features_filter).

    Parameters:
        features: Features to delete. Can be:
                 - polars.DataFrame: Features DataFrame (will use feature_uid column)
                 - list: List of feature_uids to delete
                 - int: Single feature_uid to delete

    Returns:
        None (modifies self.features_df in place)
    """
    if self.features_df is None or self.features_df.is_empty():
        self.logger.warning("No features found in study.")
        return

    # Early return if no features provided
    if features is None:
        self.logger.warning("No features provided for deletion.")
        return

    initial_count = len(self.features_df)

    # Determine feature_uids to remove - optimized type checking
    if isinstance(features, pl.DataFrame):
        if "feature_uid" not in features.columns:
            self.logger.error("features DataFrame must contain 'feature_uid' column")
            return
        feature_uids_to_remove = features["feature_uid"].to_list()
    elif isinstance(features, (list, tuple)):
        feature_uids_to_remove = list(features)  # Convert tuple to list if needed
    elif isinstance(features, int):
        feature_uids_to_remove = [features]
    else:
        self.logger.error("features parameter must be a DataFrame, list, tuple, or int")
        return

    # Early return if no UIDs to remove
    if not feature_uids_to_remove:
        self.logger.warning("No feature UIDs provided for deletion.")
        return

    # Convert to set for faster lookup if list is large
    if len(feature_uids_to_remove) > 100:
        feature_uids_set = set(feature_uids_to_remove)
        # Use the set for filtering if it's significantly smaller
        if len(feature_uids_set) < len(feature_uids_to_remove) * 0.8:
            feature_uids_to_remove = list(feature_uids_set)

    # Create filter condition - remove specified features
    filter_condition = ~pl.col("feature_uid").is_in(feature_uids_to_remove)

    # Apply filter to features_df using lazy evaluation for better performance
    self.features_df = self.features_df.lazy().filter(filter_condition).collect()

    # Apply filter to consensus_mapping_df if it exists - batch operation
    mapping_removed_count = 0
    if self.consensus_mapping_df is not None and not self.consensus_mapping_df.is_empty():
        initial_mapping_count = len(self.consensus_mapping_df)
        self.consensus_mapping_df = self.consensus_mapping_df.lazy().filter(filter_condition).collect()
        mapping_removed_count = initial_mapping_count - len(self.consensus_mapping_df)

    # Calculate results once and log efficiently
    final_count = len(self.features_df)
    removed_count = initial_count - final_count

    # Single comprehensive log message
    if mapping_removed_count > 0:
        self.logger.info(
            f"Deleted {removed_count} features and {mapping_removed_count} consensus mappings. Remaining features: {final_count}"
        )
    else:
        self.logger.info(f"Deleted {removed_count} features. Remaining features: {final_count}")


def consensus_select(
    self,
    mz=None,
    rt=None,
    inty_mean=None,
    consensus_uid=None,
    consensus_id=None,
    number_samples=None,
    number_ms2=None,
    quality=None,
    bl=None,
    chrom_coherence_mean=None,
    chrom_prominence_mean=None,
    chrom_prominence_scaled_mean=None,
    chrom_height_scaled_mean=None,
    rt_delta_mean=None,
):
    """
    Select consensus features from consensus_df based on specified criteria and return the filtered DataFrame.

    Parameters:
        mz: m/z range filter (tuple for range, single value for minimum)
        rt: retention time range filter (tuple for range, single value for minimum)
        inty_mean: mean intensity filter (tuple for range, single value for minimum)
        consensus_uid: consensus UID filter (list, single value, or tuple for range)
        consensus_id: consensus ID filter (list or single value)
        number_samples: number of samples filter (tuple for range, single value for minimum)
        number_ms2: number of MS2 spectra filter (tuple for range, single value for minimum)
        quality: quality score filter (tuple for range, single value for minimum)
        bl: baseline filter (tuple for range, single value for minimum)
        chrom_coherence_mean: mean chromatogram coherence filter (tuple for range, single value for minimum)
        chrom_prominence_mean: mean chromatogram prominence filter (tuple for range, single value for minimum)
        chrom_prominence_scaled_mean: mean scaled chromatogram prominence filter (tuple for range, single value for minimum)
        chrom_height_scaled_mean: mean scaled chromatogram height filter (tuple for range, single value for minimum)
        rt_delta_mean: mean RT delta filter (tuple for range, single value for minimum)

    Returns:
        polars.DataFrame: Filtered consensus DataFrame
    """
    if self.consensus_df is None or self.consensus_df.is_empty():
        self.logger.warning("No consensus features found in study.")
        return pl.DataFrame()

    consensus = self.consensus_df.clone()
    initial_count = len(consensus)

    # Filter by m/z
    if mz is not None:
        consensus_len_before_filter = len(consensus)
        if isinstance(mz, tuple) and len(mz) == 2:
            min_mz, max_mz = mz
            consensus = consensus.filter((pl.col("mz") >= min_mz) & (pl.col("mz") <= max_mz))
        else:
            consensus = consensus.filter(pl.col("mz") >= mz)
        self.logger.debug(
            f"Selected consensus by mz. Consensus removed: {consensus_len_before_filter - len(consensus)}",
        )

    # Filter by retention time
    if rt is not None:
        consensus_len_before_filter = len(consensus)
        if isinstance(rt, tuple) and len(rt) == 2:
            min_rt, max_rt = rt
            consensus = consensus.filter((pl.col("rt") >= min_rt) & (pl.col("rt") <= max_rt))
        else:
            consensus = consensus.filter(pl.col("rt") >= rt)
        self.logger.debug(
            f"Selected consensus by rt. Consensus removed: {consensus_len_before_filter - len(consensus)}",
        )

    # Filter by mean intensity
    if inty_mean is not None:
        consensus_len_before_filter = len(consensus)
        if isinstance(inty_mean, tuple) and len(inty_mean) == 2:
            min_inty, max_inty = inty_mean
            consensus = consensus.filter((pl.col("inty_mean") >= min_inty) & (pl.col("inty_mean") <= max_inty))
        else:
            consensus = consensus.filter(pl.col("inty_mean") >= inty_mean)
        self.logger.debug(
            f"Selected consensus by inty_mean. Consensus removed: {consensus_len_before_filter - len(consensus)}",
        )

    # Filter by consensus_uid
    if consensus_uid is not None:
        consensus_len_before_filter = len(consensus)
        if isinstance(consensus_uid, (list, tuple)):
            if len(consensus_uid) == 2 and not isinstance(consensus_uid, list):
                # Treat as range
                min_uid, max_uid = consensus_uid
                consensus = consensus.filter(
                    (pl.col("consensus_uid") >= min_uid) & (pl.col("consensus_uid") <= max_uid)
                )
            else:
                # Treat as list
                consensus = consensus.filter(pl.col("consensus_uid").is_in(consensus_uid))
        else:
            consensus = consensus.filter(pl.col("consensus_uid") == consensus_uid)
        self.logger.debug(
            f"Selected consensus by consensus_uid. Consensus removed: {consensus_len_before_filter - len(consensus)}",
        )

    # Filter by consensus_id
    if consensus_id is not None:
        consensus_len_before_filter = len(consensus)
        if isinstance(consensus_id, list):
            consensus = consensus.filter(pl.col("consensus_id").is_in(consensus_id))
        else:
            consensus = consensus.filter(pl.col("consensus_id") == consensus_id)
        self.logger.debug(
            f"Selected consensus by consensus_id. Consensus removed: {consensus_len_before_filter - len(consensus)}",
        )

    # Filter by number of samples
    if number_samples is not None:
        consensus_len_before_filter = len(consensus)
        if isinstance(number_samples, tuple) and len(number_samples) == 2:
            min_samples, max_samples = number_samples
            consensus = consensus.filter(
                (pl.col("number_samples") >= min_samples) & (pl.col("number_samples") <= max_samples)
            )
        else:
            consensus = consensus.filter(pl.col("number_samples") >= number_samples)
        self.logger.debug(
            f"Selected consensus by number_samples. Consensus removed: {consensus_len_before_filter - len(consensus)}",
        )

    # Filter by number of MS2 spectra
    if number_ms2 is not None:
        consensus_len_before_filter = len(consensus)
        if "number_ms2" in consensus.columns:
            if isinstance(number_ms2, tuple) and len(number_ms2) == 2:
                min_ms2, max_ms2 = number_ms2
                consensus = consensus.filter((pl.col("number_ms2") >= min_ms2) & (pl.col("number_ms2") <= max_ms2))
            else:
                consensus = consensus.filter(pl.col("number_ms2") >= number_ms2)
        else:
            self.logger.warning("'number_ms2' column not found in consensus_df")
        self.logger.debug(
            f"Selected consensus by number_ms2. Consensus removed: {consensus_len_before_filter - len(consensus)}",
        )

    # Filter by quality
    if quality is not None:
        consensus_len_before_filter = len(consensus)
        if isinstance(quality, tuple) and len(quality) == 2:
            min_quality, max_quality = quality
            consensus = consensus.filter((pl.col("quality") >= min_quality) & (pl.col("quality") <= max_quality))
        else:
            consensus = consensus.filter(pl.col("quality") >= quality)
        self.logger.debug(
            f"Selected consensus by quality. Consensus removed: {consensus_len_before_filter - len(consensus)}",
        )

    # Filter by baseline
    if bl is not None:
        consensus_len_before_filter = len(consensus)
        if "bl" in consensus.columns:
            if isinstance(bl, tuple) and len(bl) == 2:
                min_bl, max_bl = bl
                consensus = consensus.filter((pl.col("bl") >= min_bl) & (pl.col("bl") <= max_bl))
            else:
                consensus = consensus.filter(pl.col("bl") >= bl)
        else:
            self.logger.warning("'bl' column not found in consensus_df")
        self.logger.debug(
            f"Selected consensus by bl. Consensus removed: {consensus_len_before_filter - len(consensus)}",
        )

    # Filter by mean chromatogram coherence
    if chrom_coherence_mean is not None:
        consensus_len_before_filter = len(consensus)
        if "chrom_coherence_mean" in consensus.columns:
            if isinstance(chrom_coherence_mean, tuple) and len(chrom_coherence_mean) == 2:
                min_coherence, max_coherence = chrom_coherence_mean
                consensus = consensus.filter(
                    (pl.col("chrom_coherence_mean") >= min_coherence)
                    & (pl.col("chrom_coherence_mean") <= max_coherence)
                )
            else:
                consensus = consensus.filter(pl.col("chrom_coherence_mean") >= chrom_coherence_mean)
        else:
            self.logger.warning("'chrom_coherence_mean' column not found in consensus_df")
        self.logger.debug(
            f"Selected consensus by chrom_coherence_mean. Consensus removed: {consensus_len_before_filter - len(consensus)}",
        )

    # Filter by mean chromatogram prominence
    if chrom_prominence_mean is not None:
        consensus_len_before_filter = len(consensus)
        if "chrom_prominence_mean" in consensus.columns:
            if isinstance(chrom_prominence_mean, tuple) and len(chrom_prominence_mean) == 2:
                min_prominence, max_prominence = chrom_prominence_mean
                consensus = consensus.filter(
                    (pl.col("chrom_prominence_mean") >= min_prominence)
                    & (pl.col("chrom_prominence_mean") <= max_prominence)
                )
            else:
                consensus = consensus.filter(pl.col("chrom_prominence_mean") >= chrom_prominence_mean)
        else:
            self.logger.warning("'chrom_prominence_mean' column not found in consensus_df")
        self.logger.debug(
            f"Selected consensus by chrom_prominence_mean. Consensus removed: {consensus_len_before_filter - len(consensus)}",
        )

    # Filter by mean scaled chromatogram prominence
    if chrom_prominence_scaled_mean is not None:
        consensus_len_before_filter = len(consensus)
        if "chrom_prominence_scaled_mean" in consensus.columns:
            if isinstance(chrom_prominence_scaled_mean, tuple) and len(chrom_prominence_scaled_mean) == 2:
                min_prominence_scaled, max_prominence_scaled = chrom_prominence_scaled_mean
                consensus = consensus.filter(
                    (pl.col("chrom_prominence_scaled_mean") >= min_prominence_scaled)
                    & (pl.col("chrom_prominence_scaled_mean") <= max_prominence_scaled)
                )
            else:
                consensus = consensus.filter(pl.col("chrom_prominence_scaled_mean") >= chrom_prominence_scaled_mean)
        else:
            self.logger.warning("'chrom_prominence_scaled_mean' column not found in consensus_df")
        self.logger.debug(
            f"Selected consensus by chrom_prominence_scaled_mean. Consensus removed: {consensus_len_before_filter - len(consensus)}",
        )

    # Filter by mean scaled chromatogram height
    if chrom_height_scaled_mean is not None:
        consensus_len_before_filter = len(consensus)
        if "chrom_height_scaled_mean" in consensus.columns:
            if isinstance(chrom_height_scaled_mean, tuple) and len(chrom_height_scaled_mean) == 2:
                min_height_scaled, max_height_scaled = chrom_height_scaled_mean
                consensus = consensus.filter(
                    (pl.col("chrom_height_scaled_mean") >= min_height_scaled)
                    & (pl.col("chrom_height_scaled_mean") <= max_height_scaled)
                )
            else:
                consensus = consensus.filter(pl.col("chrom_height_scaled_mean") >= chrom_height_scaled_mean)
        else:
            self.logger.warning("'chrom_height_scaled_mean' column not found in consensus_df")
        self.logger.debug(
            f"Selected consensus by chrom_height_scaled_mean. Consensus removed: {consensus_len_before_filter - len(consensus)}",
        )

    # Filter by mean RT delta
    if rt_delta_mean is not None:
        consensus_len_before_filter = len(consensus)
        if "rt_delta_mean" in consensus.columns:
            if isinstance(rt_delta_mean, tuple) and len(rt_delta_mean) == 2:
                min_rt_delta, max_rt_delta = rt_delta_mean
                consensus = consensus.filter(
                    (pl.col("rt_delta_mean") >= min_rt_delta) & (pl.col("rt_delta_mean") <= max_rt_delta)
                )
            else:
                consensus = consensus.filter(pl.col("rt_delta_mean") >= rt_delta_mean)
        else:
            self.logger.warning("'rt_delta_mean' column not found in consensus_df")
        self.logger.debug(
            f"Selected consensus by rt_delta_mean. Consensus removed: {consensus_len_before_filter - len(consensus)}",
        )

    if len(consensus) == 0:
        self.logger.warning("No consensus features remaining after applying selection criteria.")
    else:
        self.logger.info(f"Selected consensus features. Features remaining: {len(consensus)} (from {initial_count})")

    return consensus


def consensus_filter(self, consensus):
    """
    Filter consensus_df by removing all consensus features that match the given criteria.
    This also removes related entries from consensus_mapping_df, features_df, and consensus_ms2.

    Parameters:
        consensus: Consensus features to remove. Can be:
                  - polars.DataFrame: Consensus DataFrame (will use consensus_uid column)
                  - list: List of consensus_uids to remove
                  - int: Single consensus_uid to remove

    Returns:
        None (modifies self.consensus_df and related DataFrames in place)
    """
    if self.consensus_df is None or self.consensus_df.is_empty():
        self.logger.warning("No consensus features found in study.")
        return

    initial_consensus_count = len(self.consensus_df)

    # Determine consensus_uids to remove
    if isinstance(consensus, pl.DataFrame):
        if "consensus_uid" not in consensus.columns:
            self.logger.error("consensus DataFrame must contain 'consensus_uid' column")
            return
        consensus_uids_to_remove = consensus["consensus_uid"].to_list()
    elif isinstance(consensus, list):
        consensus_uids_to_remove = consensus
    elif isinstance(consensus, int):
        consensus_uids_to_remove = [consensus]
    else:
        self.logger.error("consensus parameter must be a DataFrame, list, or int")
        return

    if not consensus_uids_to_remove:
        self.logger.warning("No consensus UIDs provided for filtering.")
        return

    # Get feature_uids that need to be removed from features_df
    feature_uids_to_remove = []
    if self.consensus_mapping_df is not None and not self.consensus_mapping_df.is_empty():
        feature_uids_to_remove = self.consensus_mapping_df.filter(
            pl.col("consensus_uid").is_in(consensus_uids_to_remove),
        )["feature_uid"].to_list()

    # Remove consensus features from consensus_df
    self.consensus_df = self.consensus_df.filter(
        ~pl.col("consensus_uid").is_in(consensus_uids_to_remove),
    )

    # Remove from consensus_mapping_df
    if self.consensus_mapping_df is not None and not self.consensus_mapping_df.is_empty():
        initial_mapping_count = len(self.consensus_mapping_df)
        self.consensus_mapping_df = self.consensus_mapping_df.filter(
            ~pl.col("consensus_uid").is_in(consensus_uids_to_remove),
        )
        removed_mapping_count = initial_mapping_count - len(self.consensus_mapping_df)
        if removed_mapping_count > 0:
            self.logger.debug(f"Removed {removed_mapping_count} entries from consensus_mapping_df")

    # Remove corresponding features from features_df
    if feature_uids_to_remove and self.features_df is not None and not self.features_df.is_empty():
        initial_features_count = len(self.features_df)
        self.features_df = self.features_df.filter(
            ~pl.col("feature_uid").is_in(feature_uids_to_remove),
        )
        removed_features_count = initial_features_count - len(self.features_df)
        if removed_features_count > 0:
            self.logger.debug(f"Removed {removed_features_count} entries from features_df")

    # Remove from consensus_ms2 if it exists
    if hasattr(self, "consensus_ms2") and self.consensus_ms2 is not None and not self.consensus_ms2.is_empty():
        initial_ms2_count = len(self.consensus_ms2)
        self.consensus_ms2 = self.consensus_ms2.filter(
            ~pl.col("consensus_uid").is_in(consensus_uids_to_remove),
        )
        removed_ms2_count = initial_ms2_count - len(self.consensus_ms2)
        if removed_ms2_count > 0:
            self.logger.debug(f"Removed {removed_ms2_count} entries from consensus_ms2")

    removed_consensus_count = initial_consensus_count - len(self.consensus_df)
    self.logger.info(
        f"Filtered {removed_consensus_count} consensus features. Remaining consensus: {len(self.consensus_df)}"
    )


def consensus_delete(self, consensus):
    """
    Delete consensus features from consensus_df based on consensus identifiers.
    This is an alias for consensus_filter for consistency with other delete methods.

    Parameters:
        consensus: Consensus features to delete. Can be:
                  - polars.DataFrame: Consensus DataFrame (will use consensus_uid column)
                  - list: List of consensus_uids to delete
                  - int: Single consensus_uid to delete

    Returns:
        None (modifies self.consensus_df and related DataFrames in place)
    """
    self.consensus_filter(consensus)
