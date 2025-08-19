from __future__ import annotations

import os
import concurrent.futures
from datetime import datetime

import numpy as np
import polars as pl
import pyopenms as oms

from tqdm import tqdm

from masster.chromatogram import Chromatogram
from masster.study.defaults import fill_defaults
from masster.sample.sample import Sample
from masster.spectrum import Spectrum


# Pre-import heavy modules to avoid repeated loading in add_sample()
try:
    import alpharaw.sciex

    ALPHARAW_AVAILABLE = True
except ImportError:
    ALPHARAW_AVAILABLE = False

try:
    import pythonnet

    PYTHONNET_AVAILABLE = True
except ImportError:
    PYTHONNET_AVAILABLE = False

import glob


def add(
    self,
    folder=None,
    reset=False,
    adducts=None,
    max_files=None,
):
    if folder is None:
        if self.folder is not None:
            folder = self.folder
        else:
            folder = os.getcwd()

    self.logger.debug(f"Adding files from: {folder}")

    # Define file extensions to search for in order of priority
    extensions = [".sample5", ".wiff", ".raw", ".mzML"]

    # Check if folder contains glob patterns
    if not any(char in folder for char in ["*", "?", "[", "]"]):
        search_folder = folder
    else:
        search_folder = os.path.dirname(folder) if os.path.dirname(folder) else folder

    # Blacklist to track filenames without extensions that have already been processed
    blacklist = set()
    counter = 0
    not_zero = False
    tdqm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]

    # Search for files in order of priority
    for ext in extensions:
        if max_files is not None and counter >= max_files:
            break

        # Build search pattern
        if any(char in folder for char in ["*", "?", "[", "]"]):
            # If folder already contains glob patterns, use it as-is
            pattern = folder
        else:
            pattern = os.path.join(search_folder, "**", f"*{ext}")

        files = glob.glob(pattern, recursive=True)

        if len(files) > 0:
            # Limit files if max_files is specified
            remaining_slots = max_files - counter if max_files is not None else len(files)
            files = files[:remaining_slots]

            self.logger.debug(f"Found {len(files)} {ext} files")

            # Process files
            for i, file in enumerate(
                tqdm(
                    files,
                    total=len(files),
                    desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Add *{ext}",
                    disable=tdqm_disable,
                ),
            ):
                if max_files is not None and counter >= max_files:
                    break

                # Get filename without extension for blacklist check
                basename = os.path.basename(file)
                filename_no_ext = os.path.splitext(basename)[0]

                # Check if this filename (without extension) is already in blacklist
                if filename_no_ext in blacklist:
                    self.logger.debug(f"Skipping {file} - filename already processed")
                    continue

                self.logger.debug(f"Add file {counter + 1}: {file}")

                # Try to add the sample
                try:
                    self.add_sample(file=file, reset=reset, adducts=adducts)
                    # If successful, add to blacklist and increment counter
                    blacklist.add(filename_no_ext)
                    counter += 1
                    not_zero = True
                except Exception as e:
                    self.logger.warning(f"Failed to add sample {file}: {e}")
                    continue

    if max_files is not None and counter >= max_files:
        self.logger.debug(
            f"Reached maximum number of files to add: {max_files}. Stopping further additions.",
        )

    if not not_zero:
        self.logger.warning(
            f"No files found in {folder}. Please check the folder path or file patterns.",
        )
    else:
        self.logger.debug(f"Successfully added {counter} samples to the study.")


# TODO type is not used
def add_sample(self, file, type=None, reset=False, adducts=None):
    self.logger.debug(f"Adding: {file}")

    # Extract sample name by removing any known extension
    basename = os.path.basename(file)
    sample_name = os.path.splitext(basename)[0]

    # check if sample_name is already in the samples_df
    if sample_name in self.samples_df["sample_name"].to_list():
        self.logger.warning(
            f"Sample {sample_name} already exists in the study. Skipping.",
        )
        return

    # check if file exists
    if not os.path.exists(file):
        self.logger.error(f"File {file} does not exist.")
        return

    # Check for supported file extensions
    if not file.endswith((".sample5", ".wiff", ".raw", ".mzML")):
        self.logger.error(f"File {file} is not a supported file type. Supported: .sample5, .wiff, .raw, .mzML")
        return

    # Load the sample based on file type
    ddaobj = Sample()
    ddaobj.logger_update(level="WARNING", label=os.path.basename(file))

    if file.endswith((".sample5", ".wiff", ".raw", ".mzML")):
        ddaobj.load(file)
    else:
        self.logger.error(f"Unsupported file format: {file}")
        return
    if ddaobj.features_df is None and not reset:
        self.logger.debug(
            f"File {file} will be newly processed.",
        )
        ddaobj.features = None

    if ddaobj.features is None or reset:
        ddaobj.find_features()
        ddaobj.find_adducts(adducts=adducts)
        ddaobj.find_ms2()

    self.features_maps.append(ddaobj.features)

    sample_type = "sample" if type is None else type
    if "qc" in sample_name.lower():
        sample_type = "qc"
    if "blank" in sample_name.lower():
        sample_type = "blank"
    map_id_value = str(ddaobj.features.getUniqueId())

    # Determine the final sample path based on file type
    if file.endswith(".sample5"):
        # If input is already .sample5, keep it in original location
        final_sample_path = file
        self.logger.debug(f"Using existing .sample5 file at original location: {final_sample_path}")

        # Check if there's a corresponding featureXML file in the same directory
        featurexml_path = file.replace(".sample5", ".featureXML")
        if os.path.exists(featurexml_path):
            self.logger.debug(f"Found corresponding featureXML file: {featurexml_path}")
        else:
            self.logger.debug(f"No corresponding featureXML file found at: {featurexml_path}")
    else:
        # For .wiff, .mzML, .raw files, save to study folder (original behavior)
        if self.folder is not None:
            if not os.path.exists(self.folder):
                os.makedirs(self.folder)
            final_sample_path = os.path.join(self.folder, sample_name + ".sample5")
            ddaobj.save(final_sample_path)
            self.logger.debug(f"Saved converted sample to study folder: {final_sample_path}")
        else:
            # If no study folder is set, save in current directory
            final_sample_path = os.path.join(os.getcwd(), sample_name + ".sample5")
            ddaobj.save(final_sample_path)
            self.logger.debug(f"Saved converted sample to current directory: {final_sample_path}")

    # Count MS1 and MS2 scans from the loaded sample
    ms1_count = 0
    ms2_count = 0
    if hasattr(ddaobj, "scans_df") and ddaobj.scans_df is not None and not ddaobj.scans_df.is_empty():
        ms1_count = int(ddaobj.scans_df.filter(pl.col("ms_level") == 1).height)
        ms2_count = int(ddaobj.scans_df.filter(pl.col("ms_level") == 2).height)

    new_sample = pl.DataFrame(
        {
            "sample_uid": [int(len(self.samples_df) + 1)],
            "sample_name": [sample_name],
            "sample_path": [final_sample_path],  # Use the determined path
            "sample_type": [sample_type],
            "size": [int(ddaobj.features.size())],
            "map_id": [map_id_value],
            "file_source": [getattr(ddaobj, "file_source", file)],
            "ms1": [ms1_count],
            "ms2": [ms2_count],
            "sample_color": [None],  # Will be set by set_sample_color below
        },
        schema={
            "sample_uid": pl.Int64,
            "sample_name": pl.Utf8,
            "sample_path": pl.Utf8,
            "sample_type": pl.Utf8,
            "size": pl.Int64,
            "map_id": pl.Utf8,
            "file_source": pl.Utf8,
            "ms1": pl.Int64,
            "ms2": pl.Int64,
            "sample_color": pl.Utf8,
        },
    )
    self.samples_df = pl.concat([self.samples_df, new_sample])

    # Optimized DataFrame operations - chain operations instead of multiple clones
    columns_to_add = [
        pl.lit(len(self.samples_df)).alias("sample_uid"),
        pl.lit(False).alias("filled"),
        pl.lit(-1.0).alias("chrom_area"),
    ]

    # Only add rt_original if it doesn't exist
    if "rt_original" not in ddaobj.features_df.columns:
        columns_to_add.append(pl.col("rt").alias("rt_original"))

    f_df = ddaobj.features_df.with_columns(columns_to_add)

    if self.features_df.is_empty():
        # Create new features_df with feature_uid column
        self.features_df = f_df.with_columns(
            pl.int_range(pl.len()).add(1).alias("feature_uid"),
        ).select(
            ["feature_uid"] + [col for col in f_df.columns if col != "feature_uid"],
        )
        # Ensure column order matches schema from the very beginning
        self._ensure_features_df_schema_order()
    else:
        offset = self.features_df["feature_uid"].max() + 1 if not self.features_df.is_empty() else 1
        # Chain operations and add to existing DataFrame
        f_df = f_df.with_columns(
            pl.int_range(pl.len()).add(offset).alias("feature_uid"),
        ).select(
            ["feature_uid"] + [col for col in f_df.columns if col != "feature_uid"],
        )
        
        # Reorganize f_df columns to match self.features_df column order and schema
        target_columns = self.features_df.columns
        target_schema = self.features_df.schema
        f_df_columns = f_df.columns

        # Create select expressions for reordering and type casting
        select_exprs = []
        for col in target_columns:
            if col in f_df_columns:
                # Cast to the expected type
                expected_dtype = target_schema[col]
                select_exprs.append(pl.col(col).cast(expected_dtype, strict=False))
            else:
                # Add missing columns with null values of the correct type
                expected_dtype = target_schema[col]
                select_exprs.append(pl.lit(None, dtype=expected_dtype).alias(col))

        # Add any extra columns from f_df that aren't in target_columns (keep their original types)
        for col in f_df_columns:
            if col not in target_columns:
                select_exprs.append(pl.col(col))

        # Reorder and type-cast f_df columns
        f_df = f_df.select(select_exprs)

        self.features_df = pl.concat([self.features_df, f_df])
            
    # Ensure features_df column order matches schema
    self._ensure_features_df_schema_order()
    
    # Auto-assign colors when new sample is added (reset all colors using turbo colormap based on UID)
    self.sample_color_reset()
    
    self.logger.debug(
        f"Added sample {sample_name} with {ddaobj.features.size()} features to the study.",
    )


def load(self, filename=None):
    """
    Load a study from an HDF5 file.

    Args:
        study: The study object to load into
        filename (str, optional): The path to the HDF5 file to load the study from.
    """

    # Handle default filename
    if filename is None:
        if self.folder is not None:
            # search for *.study5 in folder
            study5_files = glob.glob(os.path.join(self.folder, "*.study5"))
            if study5_files:
                filename = study5_files[-1]
            else:
                self.logger.error("No .study5 files found in folder")
                return
        else:
            self.logger.error("Either filename or folder must be provided")
            return

    # self.logger.info(f"Loading study from {filename}")
    self._load_study5(filename)
    # After loading the study, check if consensus XML exists and load it
    consensus_xml_path = filename.replace(".study5", ".consensusXML")
    if os.path.exists(consensus_xml_path):
        self._load_consensusXML(filename=consensus_xml_path)
        # self.logger.info(f"Automatically loaded consensus from {consensus_xml_path}")
    else:
        self.logger.warning(f"No consensus XML file found at {consensus_xml_path}")
    self.filename = filename


def _fill_chrom_single_impl(
    self,
    uids=None,
    mz_tol: float = 0.010,
    rt_tol: float = 10.0,
    min_samples_rel: float = 0.0,
    min_samples_abs: int = 2,
):
    """Fill missing chromatograms by extracting from raw data.

    Simplified version that loads one sample at a time without preloading or batching.

    Args:
        uids: Consensus UIDs to process (default: all)
        mz_tol: m/z tolerance for extraction (default: 0.010 Da)
        rt_tol: RT tolerance for extraction (default: 10.0 seconds)
        min_samples_rel: Relative minimum sample threshold (default: 0.0)
        min_samples_abs: Absolute minimum sample threshold (default: 2)
    """
    uids = self._get_consensus_uids(uids)

    self.logger.info("Gap filling...")
    self.logger.debug(
        f"Parameters: mz_tol={mz_tol}, rt_tol={rt_tol}, min_samples_rel={min_samples_rel}, min_samples_abs={min_samples_abs}",
    )

    # Apply minimum sample filters
    min_number_rel = 1
    min_number_abs = 1
    if isinstance(min_samples_rel, float) and min_samples_rel > 0:
        min_number_rel = int(min_samples_rel * len(self.samples_df))
    if isinstance(min_samples_abs, int) and min_samples_abs > 0:
        min_number_abs = int(min_samples_abs)
    min_number = max(min_number_rel, min_number_abs)
    self.logger.debug(f"Threshold for gap filling: number_samples>={min_number}")

    if min_number > 0:
        original_count = len(uids)
        uids = self.consensus_df.filter(
            (pl.col("number_samples") >= min_number) & (pl.col("consensus_uid").is_in(uids)),
        )["consensus_uid"].to_list()
        self.logger.debug(
            f"Features to fill: {original_count} -> {len(uids)}",
        )
    self.logger.debug("Identifying missing features...")
    # Instead of building full chromatogram matrix, identify missing consensus/sample combinations directly
    missing_combinations = self._get_missing_consensus_sample_combinations(uids)
    if not missing_combinations:
        self.logger.info("No missing features found to fill.")
        return

    # Build lookup dictionaries
    self.logger.debug("Building lookup dictionaries...")
    consensus_info = {}
    consensus_subset = self.consensus_df.select([
        "consensus_uid",
        "rt_start_mean",
        "rt_end_mean",
        "mz",
        "rt",
    ]).filter(pl.col("consensus_uid").is_in(uids))

    for row in consensus_subset.iter_rows(named=True):
        consensus_info[row["consensus_uid"]] = {
            "rt_start_mean": row["rt_start_mean"],
            "rt_end_mean": row["rt_end_mean"],
            "mz": row["mz"],
            "rt": row["rt"],
        }

    # Process each sample individually
    # Group missing combinations by sample for efficient processing
    missing_by_sample = {}
    for consensus_uid, sample_uid, sample_name, sample_path in missing_combinations:
        if sample_name not in missing_by_sample:
            missing_by_sample[sample_name] = {
                "sample_uid": sample_uid,
                "sample_path": sample_path,
                "missing_consensus_uids": [],
            }
        missing_by_sample[sample_name]["missing_consensus_uids"].append(consensus_uid)

    new_features: list[dict] = []
    new_mapping: list[dict] = []
    counter = 0

    self.logger.debug(
        f"Missing features: {len(missing_combinations)} in {len(missing_by_sample)} samples...",
    )

    tdqm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]

    for sample_name, sample_info in tqdm(
        missing_by_sample.items(),
        desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}File",
        disable=tdqm_disable,
    ):
        # Load this sample
        sample_uid = sample_info["sample_uid"]
        sample_path = sample_info["sample_path"]
        missing_consensus_uids = sample_info["missing_consensus_uids"]

        try:
            # self.logger.debug(f"Loading sample: {sample_path}")
            file = Sample()
            file.logger_update("WARNING")
            file.load(sample_path)
        except Exception as e:
            self.logger.warning(f"Failed to load sample {sample_name}: {e}")
            continue

        self.logger.debug(
            f"Sample {sample_name}: Processing {len(missing_consensus_uids)} missing features",
        )

        # Process each missing feature
        for consensus_uid in missing_consensus_uids:
            cons = consensus_info[consensus_uid]
            mz = cons["mz"]
            rt = cons["rt"]
            rt_start_mean = cons["rt_start_mean"]
            rt_end_mean = cons["rt_end_mean"]

            # Filter MS1 data for this feature
            if hasattr(file, "ms1_df") and not file.ms1_df.is_empty():
                d = file.ms1_df.filter(
                    (pl.col("mz") >= mz - mz_tol)
                    & (pl.col("mz") <= mz + mz_tol)
                    & (pl.col("rt") >= rt_start_mean - rt_tol)
                    & (pl.col("rt") <= rt_end_mean + rt_tol),
                )
            else:
                d = pl.DataFrame()

            # Create chromatogram
            if d.is_empty():
                self.logger.debug(
                    f"Feature {consensus_uid}: No MS1 data found, creating empty chromatogram",
                )
                eic = Chromatogram(
                    rt=np.array([rt_start_mean, rt_end_mean]),
                    inty=np.array([0.0, 0.0]),
                    label=f"EIC mz={mz:.4f}",
                    file=sample_path,
                    mz=mz,
                    mz_tol=mz_tol,
                    feature_start=rt_start_mean,
                    feature_end=rt_end_mean,
                    feature_apex=rt,
                )
                max_inty = 0.0
                area = 0.0
            else:
                self.logger.debug(
                    f"Feature {consensus_uid}: Found {len(d)} MS1 points, creating EIC",
                )
                eic_rt = d.group_by("rt").agg(pl.col("inty").max()).sort("rt")

                if len(eic_rt) > 4:
                    eic = Chromatogram(
                        eic_rt["rt"].to_numpy(),
                        eic_rt["inty"].to_numpy(),
                        label=f"EIC mz={mz:.4f}",
                        file=sample_path,
                        mz=mz,
                        mz_tol=mz_tol,
                        feature_start=rt_start_mean,
                        feature_end=rt_end_mean,
                        feature_apex=rt,
                    ).find_peaks()
                    max_inty = np.max(eic.inty)
                    area = eic.feature_area
                else:
                    eic = Chromatogram(
                        eic_rt["rt"].to_numpy(),
                        eic_rt["inty"].to_numpy(),
                        label=f"EIC mz={mz:.4f}",
                        file=sample_path,
                        mz=mz,
                        mz_tol=mz_tol,
                        feature_start=rt_start_mean,
                        feature_end=rt_end_mean,
                        feature_apex=rt,
                    )
                    max_inty = 0.0
                    area = 0.0

            # Generate feature UID
            feature_uid = (
                self.features_df["feature_uid"].max() + len(new_features) + 1
                if not self.features_df.is_empty()
                else len(new_features) + 1
            )

            # Create new feature entry
            new_feature = {
                "sample_uid": sample_uid,
                "feature_uid": feature_uid,
                "feature_id": None,
                "mz": mz,
                "rt": rt,
                "rt_original": None,
                "rt_start": rt_start_mean,
                "rt_end": rt_end_mean,
                "rt_delta": rt_end_mean - rt_start_mean,
                "mz_start": None,
                "mz_end": None,
                "inty": max_inty,
                "quality": None,
                "charge": None,
                "iso": None,
                "iso_of": None,
                "adduct": None,
                "adduct_mass": None,
                "adduct_group": None,
                "chrom": eic,
                "chrom_coherence": None,
                "chrom_prominence": None,
                "chrom_prominence_scaled": None,
                "chrom_height_scaled": None,
                "ms2_scans": None,
                "ms2_specs": None,
                "filled": True,
                "chrom_area": area,
            }

            new_features.append(new_feature)
            new_mapping.append({
                "consensus_uid": consensus_uid,
                "sample_uid": sample_uid,
                "feature_uid": feature_uid,
            })
            counter += 1

    # Add new features to DataFrames
    self.logger.debug(f"Adding {len(new_features)} new features to DataFrame...")
    if new_features:
        # Create properly formatted rows
        rows_to_add = []
        for feature_dict in new_features:
            new_row = {}
            for col in self.features_df.columns:
                if col in feature_dict:
                    new_row[col] = feature_dict[col]
                else:
                    new_row[col] = None
            rows_to_add.append(new_row)

        # Create and add new DataFrame
        if rows_to_add:
            # Ensure consistent data types by explicitly casting problematic columns
            for row in rows_to_add:
                # Cast numeric columns to ensure consistency
                for key, value in row.items():
                    if key in ["mz", "rt", "intensity", "area", "height"] and value is not None:
                        row[key] = float(value)
                    elif key in ["sample_id", "feature_id"] and value is not None:
                        row[key] = int(value)

            new_df = pl.from_dicts(rows_to_add, infer_schema_length=len(rows_to_add))
        else:
            # Handle empty case - create empty DataFrame with proper schema
            new_df = pl.DataFrame(schema=self.features_df.schema)

        # Cast columns to match existing schema
        cast_exprs = []
        for col in self.features_df.columns:
            existing_dtype = self.features_df[col].dtype
            cast_exprs.append(pl.col(col).cast(existing_dtype, strict=False))

        new_df = new_df.with_columns(cast_exprs)
        self.features_df = self.features_df.vstack(new_df)

        # Add consensus mapping
        new_mapping_df = pl.DataFrame(new_mapping)
        self.consensus_mapping_df = pl.concat(
            [self.consensus_mapping_df, new_mapping_df],
            how="diagonal",
        )

    self.logger.info(f"Filled {counter} chromatograms from raw data.")


def fill_single(self, **kwargs):
    """Fill missing chromatograms by extracting from raw data.

    Simplified version that loads one sample at a time without preloading or batching.

    Parameters:
        **kwargs: Keyword arguments for fill_single parameters. Can include:
            - A fill_defaults instance to set all parameters at once
            - Individual parameter names and values (see fill_defaults for details)

    Key Parameters:
        uids: Consensus UIDs to process (default: all)
        mz_tol: m/z tolerance for extraction (default: 0.010 Da)
        rt_tol: RT tolerance for extraction (default: 10.0 seconds)
        min_samples_rel: Relative minimum sample threshold (default: 0.0)
        min_samples_abs: Absolute minimum sample threshold (default: 2)
    """
    # parameters initialization
    from masster.study.defaults import fill_defaults

    params = fill_defaults()

    for key, value in kwargs.items():
        if isinstance(value, fill_defaults):
            params = value
            self.logger.debug("Using provided fill_defaults parameters")
        else:
            if hasattr(params, key):
                if params.set(key, value, validate=True):
                    self.logger.debug(f"Updated parameter {key} = {value}")
                else:
                    self.logger.warning(
                        f"Failed to set parameter {key} = {value} (validation failed)",
                    )
            else:
                self.logger.debug(f"Unknown parameter {key} ignored")
    # end of parameter initialization

    # Store parameters in the Study object
    self.store_history(["fill_single"], params.to_dict())
    self.logger.debug("Parameters stored to fill_single")

    # Call the original fill_chrom_single function with extracted parameters
    return _fill_chrom_single_impl(
        self,
        uids=params.get("uids"),
        mz_tol=params.get("mz_tol"),
        rt_tol=params.get("rt_tol"),
        min_samples_rel=params.get("min_samples_rel"),
        min_samples_abs=params.get("min_samples_abs"),
    )


def _process_sample_for_parallel_fill(
    self,
    sample_info,
    consensus_info,
    uids,
    mz_tol,
    rt_tol,
    missing_combinations_df,
    features_df_max_uid,
):
    """Process a single sample for parallel gap filling."""
    sample_uid = sample_info["sample_uid"]
    sample_path = sample_info["sample_path"]

    new_features: list[dict] = []
    new_mapping: list[dict] = []
    counter = 0

    try:
        # Load this sample
        file = Sample()
        file.logger_update(level="WARNING")
        file.load(sample_path)
    except Exception:
        # Skip this sample if loading fails
        return new_features, new_mapping, counter

    # Find missing features for this sample from precomputed combinations
    sample_missing = missing_combinations_df.filter(
        pl.col("sample_uid") == sample_uid,
    )["consensus_uid"].to_list()

    if not sample_missing:
        return new_features, new_mapping, counter

    # Process each missing feature
    for consensus_uid in sample_missing:
        cons = consensus_info[consensus_uid]
        mz = cons["mz"]
        rt = cons["rt"]
        rt_start_mean = cons["rt_start_mean"]
        rt_end_mean = cons["rt_end_mean"]

        # Filter MS1 data for this feature
        if hasattr(file, "ms1_df") and not file.ms1_df.is_empty():
            d = file.ms1_df.filter(
                (pl.col("mz") >= mz - mz_tol)
                & (pl.col("mz") <= mz + mz_tol)
                & (pl.col("rt") >= rt_start_mean - rt_tol)
                & (pl.col("rt") <= rt_end_mean + rt_tol),
            )
        else:
            d = pl.DataFrame()

        # Create chromatogram
        if d.is_empty():
            eic = Chromatogram(
                rt=np.array([rt_start_mean, rt_end_mean]),
                inty=np.array([0.0, 0.0]),
                label=f"EIC mz={mz:.4f}",
                file=sample_path,
                mz=mz,
                mz_tol=mz_tol,
                feature_start=rt_start_mean,
                feature_end=rt_end_mean,
                feature_apex=rt,
            )
            max_inty = 0.0
            area = 0.0
        else:
            eic_rt = d.group_by("rt").agg(pl.col("inty").max()).sort("rt")

            if len(eic_rt) > 4:
                eic = Chromatogram(
                    eic_rt["rt"].to_numpy(),
                    eic_rt["inty"].to_numpy(),
                    label=f"EIC mz={mz:.4f}",
                    file=sample_path,
                    mz=mz,
                    mz_tol=mz_tol,
                    feature_start=rt_start_mean,
                    feature_end=rt_end_mean,
                    feature_apex=rt,
                ).find_peaks()
                max_inty = np.max(eic.inty)
                area = eic.feature_area
            else:
                eic = Chromatogram(
                    eic_rt["rt"].to_numpy(),
                    eic_rt["inty"].to_numpy(),
                    label=f"EIC mz={mz:.4f}",
                    file=sample_path,
                    mz=mz,
                    mz_tol=mz_tol,
                    feature_start=rt_start_mean,
                    feature_end=rt_end_mean,
                    feature_apex=rt,
                )
                max_inty = 0.0
                area = 0.0

        # Generate feature UID (will be adjusted later to ensure global uniqueness)
        feature_uid = features_df_max_uid + len(new_features) + 1

        # Create new feature entry
        new_feature = {
            "sample_uid": sample_uid,
            "feature_uid": feature_uid,
            "feature_id": None,
            "mz": mz,
            "rt": rt,
            "rt_original": None,
            "rt_start": rt_start_mean,
            "rt_end": rt_end_mean,
            "rt_delta": rt_end_mean - rt_start_mean,
            "mz_start": None,
            "mz_end": None,
            "inty": max_inty,
            "quality": None,
            "charge": None,
            "iso": None,
            "iso_of": None,
            "adduct": None,
            "adduct_mass": None,
            "adduct_group": None,
            "chrom": eic,
            "filled": True,
            "chrom_area": area,
            "chrom_coherence": None,
            "chrom_prominence": None,
            "chrom_prominence_scaled": None,
            "chrom_height_scaled": None,
            "ms2_scans": None,
            "ms2_specs": None,
        }

        new_features.append(new_feature)
        new_mapping.append({
            "consensus_uid": consensus_uid,
            "sample_uid": sample_uid,
            "feature_uid": feature_uid,
        })
        counter += 1

    return new_features, new_mapping, counter


def _fill_chrom_impl(
    self,
    uids=None,
    mz_tol: float = 0.010,
    rt_tol: float = 10.0,
    min_samples_rel: float = 0.0,
    min_samples_abs: int = 2,
    num_workers=4,
):
    """Fill missing chromatograms by extracting from raw data using parallel processing.

    Args:
        uids: Consensus UIDs to process (default: all)
        mz_tol: m/z tolerance for extraction (default: 0.010 Da)
        rt_tol: RT tolerance for extraction (default: 10.0 seconds)
        min_samples_rel: Relative minimum sample threshold (default: 0.0)
        min_samples_abs: Absolute minimum sample threshold (default: 2)
        num_workers: Number of parallel workers (default: 4)
    """
    uids = self._get_consensus_uids(uids)

    self.logger.info(f"Gap filling with {num_workers} workers...")
    self.logger.debug(
        f"Parameters: mz_tol={mz_tol}, rt_tol={rt_tol}, min_samples_rel={min_samples_rel}, min_samples_abs={min_samples_abs}, num_workers={num_workers}",
    )

    # Apply minimum sample filters
    min_number_rel = 1
    min_number_abs = 1
    if isinstance(min_samples_rel, float) and min_samples_rel > 0:
        min_number_rel = int(min_samples_rel * len(self.samples_df))
    if isinstance(min_samples_abs, int) and min_samples_abs > 0:
        min_number_abs = int(min_samples_abs)
    min_number = max(min_number_rel, min_number_abs)

    self.logger.debug(f"Threshold for gap filling: number_samples>={min_number}")

    if min_number > 0:
        original_count = len(uids)
        uids = self.consensus_df.filter(
            (pl.col("number_samples") >= min_number) & (pl.col("consensus_uid").is_in(uids)),
        )["consensus_uid"].to_list()
        self.logger.debug(f"Features to fill: {original_count} -> {len(uids)}")

    # Get missing consensus/sample combinations using the optimized method
    self.logger.debug("Identifying missing features...")
    missing_combinations = self._get_missing_consensus_sample_combinations(uids)

    if not missing_combinations or len(missing_combinations) == 0:
        self.logger.info("No missing features found to fill.")
        return

    # Convert to DataFrame for easier processing
    missing_combinations_df = pl.DataFrame(
        missing_combinations,
        schema={
            "consensus_uid": pl.Int64,
            "sample_uid": pl.Int64,
            "sample_name": pl.Utf8,
            "sample_path": pl.Utf8,
        },
        orient="row",
    )

    # Build lookup dictionaries
    self.logger.debug("Building lookup dictionaries...")
    consensus_info = {}
    consensus_subset = self.consensus_df.select([
        "consensus_uid",
        "rt_start_mean",
        "rt_end_mean",
        "mz",
        "rt",
    ]).filter(pl.col("consensus_uid").is_in(uids))

    for row in consensus_subset.iter_rows(named=True):
        consensus_info[row["consensus_uid"]] = {
            "rt_start_mean": row["rt_start_mean"],
            "rt_end_mean": row["rt_end_mean"],
            "mz": row["mz"],
            "rt": row["rt"],
        }

    # Get sample info for all samples that need processing
    samples_to_process = []
    unique_sample_uids = missing_combinations_df["sample_uid"].unique().to_list()

    for row in self.samples_df.filter(
        pl.col("sample_uid").is_in(unique_sample_uids),
    ).iter_rows(named=True):
        samples_to_process.append({
            "sample_name": row["sample_name"],
            "sample_uid": row["sample_uid"],
            "sample_path": row["sample_path"],
        })

    total_missing = len(missing_combinations_df)
    total_samples = len(samples_to_process)

    self.logger.debug(
        f"Gap filling for {total_missing} missing features...",
    )

    # Calculate current max feature_uid to avoid conflicts
    features_df_max_uid = self.features_df["feature_uid"].max() if not self.features_df.is_empty() else 0

    # Process samples in parallel
    all_new_features: list[dict] = []
    all_new_mapping: list[dict] = []
    total_counter = 0

    tdqm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        # Submit all samples for processing
        future_to_sample = {}
        for sample_info in samples_to_process:
            future = executor.submit(
                self._process_sample_for_parallel_fill,
                sample_info,
                consensus_info,
                uids,
                mz_tol,
                rt_tol,
                missing_combinations_df,
                features_df_max_uid,
            )
            future_to_sample[future] = sample_info

        # Collect results with progress bar
        with tqdm(
            total=len(samples_to_process),
            desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Processing samples",
            disable=tdqm_disable,
        ) as pbar:
            for future in concurrent.futures.as_completed(future_to_sample):
                try:
                    new_features, new_mapping, counter = future.result()

                    # Adjust feature UIDs to ensure global uniqueness
                    uid_offset = features_df_max_uid + len(all_new_features)
                    for i, feature in enumerate(new_features):
                        feature["feature_uid"] = uid_offset + i + 1
                    for i, mapping in enumerate(new_mapping):
                        mapping["feature_uid"] = uid_offset + i + 1

                    all_new_features.extend(new_features)
                    all_new_mapping.extend(new_mapping)
                    total_counter += counter

                except Exception as e:
                    sample_info = future_to_sample[future]
                    self.logger.warning(
                        f"Sample {sample_info['sample_name']} failed: {e}",
                    )

                pbar.update(1)

    # Add new features to DataFrames
    self.logger.debug(f"Adding {len(all_new_features)} new features to DataFrame...")
    if all_new_features:
        # Create properly formatted rows
        rows_to_add = []
        for feature_dict in all_new_features:
            new_row = {}
            for col in self.features_df.columns:
                if col in feature_dict:
                    new_row[col] = feature_dict[col]
                else:
                    new_row[col] = None
            rows_to_add.append(new_row)

        # Create and add new DataFrame
        if rows_to_add:
            # Ensure consistent data types by explicitly casting problematic columns
            for row in rows_to_add:
                # Cast numeric columns to ensure consistency
                for key, value in row.items():
                    if key in ["mz", "rt", "intensity", "area", "height"] and value is not None:
                        row[key] = float(value)
                    elif key in ["sample_id", "feature_id"] and value is not None:
                        row[key] = int(value)

            new_df = pl.from_dicts(rows_to_add, infer_schema_length=len(rows_to_add))
        else:
            # Handle empty case - create empty DataFrame with proper schema
            new_df = pl.DataFrame(schema=self.features_df.schema)

        # Cast columns to match existing schema
        cast_exprs = []
        for col in self.features_df.columns:
            existing_dtype = self.features_df[col].dtype
            cast_exprs.append(pl.col(col).cast(existing_dtype, strict=False))

        new_df = new_df.with_columns(cast_exprs)
        self.features_df = self.features_df.vstack(new_df)

        # Add consensus mapping
        new_mapping_df = pl.DataFrame(all_new_mapping)
        self.consensus_mapping_df = pl.concat(
            [self.consensus_mapping_df, new_mapping_df],
            how="diagonal",
        )

    self.logger.info(
        f"Filled {total_counter} chromatograms from raw data using {num_workers} parallel workers.",
    )


def fill(self, **kwargs):
    """Fill missing chromatograms by extracting from raw data using parallel processing.

    Parameters:
        **kwargs: Keyword arguments for fill parameters. Can include:
            - A fill_defaults instance to set all parameters at once
            - Individual parameter names and values (see fill_defaults for details)

    Key Parameters:
        uids: Consensus UIDs to process (default: all)
        mz_tol: m/z tolerance for extraction (default: 0.010 Da)
        rt_tol: RT tolerance for extraction (default: 10.0 seconds)
        min_samples_rel: Relative minimum sample threshold (default: 0.05)
        min_samples_abs: Absolute minimum sample threshold (default: 5)
        num_workers: Number of parallel workers (default: 4)
    """
    # parameters initialization
    params = fill_defaults()
    num_workers = kwargs.get("num_workers", 4)  # Default parameter not in defaults class

    for key, value in kwargs.items():
        if isinstance(value, fill_defaults):
            params = value
            self.logger.debug("Using provided fill_defaults parameters")
        else:
            if hasattr(params, key):
                if params.set(key, value, validate=True):
                    self.logger.debug(f"Updated parameter {key} = {value}")
                else:
                    self.logger.warning(
                        f"Failed to set parameter {key} = {value} (validation failed)",
                    )
            elif key != "num_workers":  # Allow num_workers as valid parameter
                self.logger.debug(f"Unknown parameter {key} ignored")
    # end of parameter initialization

    # Store parameters in the Study object
    self.store_history(["fill"], params.to_dict())
    self.logger.debug("Parameters stored to fill")

    # Call the original fill_chrom function with extracted parameters
    return _fill_chrom_impl(
        self,
        uids=params.get("uids"),
        mz_tol=params.get("mz_tol"),
        rt_tol=params.get("rt_tol"),
        min_samples_rel=params.get("min_samples_rel"),
        min_samples_abs=params.get("min_samples_abs"),
        num_workers=num_workers,
    )


# Backward compatibility alias
fill_chrom = fill


def _get_missing_consensus_sample_combinations(self, uids):
    """
    Efficiently identify which consensus_uid/sample combinations are missing.
    Returns a list of tuples: (consensus_uid, sample_uid, sample_name, sample_path)
    """
    # Get all consensus UIDs we're interested in
    consensus_uids_set = set(uids)

    # Get all sample UIDs and create lookup
    all_sample_info = {}
    for row in self.samples_df.select([
        "sample_uid",
        "sample_name",
        "sample_path",
    ]).iter_rows(named=True):
        all_sample_info[row["sample_uid"]] = {
            "sample_name": row["sample_name"],
            "sample_path": row["sample_path"],
        }

    # Get existing consensus/sample combinations from consensus_mapping_df
    existing_combinations = set()
    consensus_mapping_filtered = self.consensus_mapping_df.filter(
        pl.col("consensus_uid").is_in(list(consensus_uids_set)),
    )

    # Join with features_df to get sample_uid information
    existing_features = consensus_mapping_filtered.join(
        self.features_df.select(["feature_uid", "sample_uid"]),
        on="feature_uid",
        how="inner",
    )

    for row in existing_features.select(["consensus_uid", "sample_uid"]).iter_rows():
        existing_combinations.add((row[0], row[1]))  # (consensus_uid, sample_uid)

    # Find missing combinations
    missing_combinations = []
    for consensus_uid in consensus_uids_set:
        for sample_uid, sample_info in all_sample_info.items():
            if (consensus_uid, sample_uid) not in existing_combinations:
                missing_combinations.append((
                    consensus_uid,
                    sample_uid,
                    sample_info["sample_name"],
                    sample_info["sample_path"],
                ))

    return missing_combinations


def sanitize(self):
    """
    Sanitize features DataFrame to ensure all complex objects are properly typed.
    Convert serialized objects back to their proper types (Chromatogram, Spectrum).
    """
    if self.features_df is None or self.features_df.is_empty():
        return

    self.logger.debug(
        "Sanitizing features DataFrame to ensure all complex objects are properly typed.",
    )
    tdqm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]

    # Check if we have object columns that need sanitization
    has_chrom = "chrom" in self.features_df.columns
    has_ms2_specs = "ms2_specs" in self.features_df.columns

    if not has_chrom and not has_ms2_specs:
        self.logger.debug("No object columns found that need sanitization.")
        return

    # Convert to list of dictionaries for easier manipulation
    rows_data = []

    for row_dict in tqdm(
        self.features_df.iter_rows(named=True),
        total=len(self.features_df),
        desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     |{self.log_label}Sanitize features",
        disable=tdqm_disable,
    ):
        row_data = dict(row_dict)

        # Sanitize chrom column
        if has_chrom and row_data["chrom"] is not None:
            if not isinstance(row_data["chrom"], Chromatogram):
                try:
                    # Create new Chromatogram and populate from dict if needed
                    new_chrom = Chromatogram(rt=np.array([]), inty=np.array([]))
                    if hasattr(row_data["chrom"], "__dict__"):
                        new_chrom.from_dict(row_data["chrom"].__dict__)
                    else:
                        # If it's already a dict
                        new_chrom.from_dict(row_data["chrom"])
                    row_data["chrom"] = new_chrom
                except Exception as e:
                    self.logger.warning(f"Failed to sanitize chrom object: {e}")
                    row_data["chrom"] = None

        # Sanitize ms2_specs column
        if has_ms2_specs and row_data["ms2_specs"] is not None:
            if isinstance(row_data["ms2_specs"], list):
                sanitized_specs = []
                for ms2_specs in row_data["ms2_specs"]:
                    if not isinstance(ms2_specs, Spectrum):
                        try:
                            new_ms2_specs = Spectrum(mz=np.array([0]), inty=np.array([0]))
                            if hasattr(ms2_specs, "__dict__"):
                                new_ms2_specs.from_dict(ms2_specs.__dict__)
                            else:
                                new_ms2_specs.from_dict(ms2_specs)
                            sanitized_specs.append(new_ms2_specs)
                        except Exception as e:
                            self.logger.warning(
                                f"Failed to sanitize ms2_specs object: {e}",
                            )
                            sanitized_specs.append(None)
                    else:
                        sanitized_specs.append(ms2_specs)
                row_data["ms2_specs"] = sanitized_specs
            elif not isinstance(row_data["ms2_specs"], Spectrum):
                try:
                    new_ms2_specs = Spectrum(mz=np.array([0]), inty=np.array([0]))
                    if hasattr(row_data["ms2_specs"], "__dict__"):
                        new_ms2_specs.from_dict(row_data["ms2_specs"].__dict__)
                    else:
                        new_ms2_specs.from_dict(row_data["ms2_specs"])
                    row_data["ms2_specs"] = new_ms2_specs
                except Exception as e:
                    self.logger.warning(f"Failed to sanitize ms2_specs object: {e}")
                    row_data["ms2_specs"] = None

        rows_data.append(row_data)

    # Recreate the DataFrame with sanitized data
    try:
        self.features_df = pl.DataFrame(rows_data)
        self.logger.success("Features DataFrame sanitization completed successfully.")
    except Exception as e:
        self.logger.error(f"Failed to recreate sanitized DataFrame: {e}")


def load_features(self):
    # iterate over all samples in samples_df

    self.features_maps = []
    self.logger.debug("Loading features from featureXML files.")
    tdqm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]
    for _index, row_dict in tqdm(
        enumerate(self.samples_df.iter_rows(named=True)),
        total=len(self.samples_df),
        desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Load feature maps from XML",
        disable=tdqm_disable,
    ):
        if self.folder is not None:
            filename = os.path.join(
                self.folder,
                row_dict["sample_name"] + ".featureXML",
            )
        else:
            filename = os.path.join(
                os.getcwd(),
                row_dict["sample_name"] + ".featureXML",
            )
        # check if file exists
        if not os.path.exists(filename):
            filename = row_dict["sample_path"].replace(".sample5", ".featureXML")

        if not os.path.exists(filename):
            self.features_maps.append(None)
            continue

        fh = oms.FeatureXMLFile()
        fm = oms.FeatureMap()
        fh.load(filename, fm)
        self.features_maps.append(fm)
    self.logger.debug("Features loaded successfully.")


def _load_consensusXML(self, filename="alignment.consensusXML"):
    """
    Load a consensus map from a file.
    """
    if not os.path.exists(filename):
        self.logger.error(f"File {filename} does not exist.")
        return
    fh = oms.ConsensusXMLFile()
    self.consensus_map = oms.ConsensusMap()
    fh.load(filename, self.consensus_map)
    self.logger.debug(f"Loaded consensus map from {filename}.")
