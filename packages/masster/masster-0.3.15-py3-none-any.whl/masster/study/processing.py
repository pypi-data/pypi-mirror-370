from __future__ import annotations

from datetime import datetime

import numpy as np
import polars as pl
import pyopenms as oms

from tqdm import tqdm

from masster.study.defaults import (
    align_defaults,
    find_ms2_defaults,
    integrate_defaults,
    merge_defaults,
)


def align(self, **kwargs):
    """Align feature maps using pose clustering or KD algorithm and update feature RTs.

    Parameters can be provided as an ``align_defaults`` instance or as
    individual keyword arguments; they are validated against the defaults class.

    Key parameters (from ``align_defaults``):
        - rt_max_diff (float): Maximum RT difference for pair finding (seconds).
        - mz_max_diff (float): Maximum m/z difference for pair finding (Da).
        - rt_pair_distance_frac (float): RT fraction used by the superimposer.
        - mz_pair_max_distance (float): Max m/z distance for pair selection.
        - num_used_points (int): Number of points to use for alignment estimation.
        - save_features (bool): If True, save updated features after alignment.
        - skip_blanks (bool): If True, skip blank samples during alignment.
        - algo (str): Alignment algorithm ('pc' for PoseClustering, 'kd' for KD).

        KD algorithm specific parameters:
        - nr_partitions (int): Number of partitions in m/z dimension.
        - warp_enabled (bool): Enable non-linear retention time transformation.
        - warp_rt_tol (float): RT tolerance for the LOWESS fit.
        - warp_mz_tol (float): m/z tolerance for the LOWESS fit.
        - warp_max_pairwise_log_fc (float): Maximum absolute log10 fold-change threshold for pairing.
        - warp_min_rel_cc_size (float): Minimum relative connected component size.
        - warp_max_nr_conflicts (int): Allow up to this many conflicts per connected component for alignment.
        - link_rt_tol (float): Width of RT tolerance window for linking features.
        - link_mz_tol (float): m/z tolerance for linking features.
        - link_charge_merging (str): Charge merging strategy for linking features.
        - link_adduct_merging (str): Adduct merging strategy for linking features.
        - distance_RT_exponent (float): Exponent for normalized RT differences.
        - distance_RT_weight (float): Weight factor for final RT distances.
        - distance_MZ_exponent (float): Exponent for normalized m/z differences.
        - distance_MZ_weight (float): Weight factor for final m/z distances.
        - distance_intensity_exponent (float): Exponent for differences in relative intensity.
        - distance_intensity_weight (float): Weight factor for final intensity distances.
        - distance_intensity_log_transform (str): Log-transform intensities.
        - LOWESS_span (float): Fraction of datapoints for each local regression.
        - LOWESS_num_iterations (int): Number of robustifying iterations for LOWESS fitting.
        - LOWESS_delta (float): Parameter for LOWESS computations (negative auto-computes).
        - LOWESS_interpolation_type (str): Method for interpolation between datapoints.
        - LOWESS_extrapolation_type (str): Method for extrapolation outside data range.
    """
    # parameters initialization
    params = align_defaults()
    for key, value in kwargs.items():
        if isinstance(value, align_defaults):
            params = value
            self.logger.debug("Using provided align_defaults parameters")
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
    self.store_history(["align"], params.to_dict())
    self.logger.debug("Parameters stored to align")

    if len(self.features_maps) < len(self.samples_df):
        self.features_maps = []
        self.load_features()

    # self.logger.debug("Starting alignment")

    fmaps = self.features_maps

    # Initialize OpenMS parameters
    params_oms = oms.Param()
    # Choose alignment algorithm based on parameter
    algo = params.get("algo").lower()

    # Set common parameters for both algorithms
    if algo == "pc":
        # Parameters specific to PoseClustering
        params_oms.setValue("pairfinder:distance_intensity:log_transform", "disabled")
        params_oms.setValue("pairfinder:ignore_charge", "true")
        params_oms.setValue("max_num_peaks_considered", 1000)
        params_oms.setValue("pairfinder:distance_RT:max_difference", params.get("rt_max_diff"))
        params_oms.setValue("pairfinder:distance_MZ:max_difference", params.get("mz_max_diff"))
        params_oms.setValue("superimposer:rt_pair_distance_fraction", params.get("rt_pair_distance_frac"))
        params_oms.setValue("superimposer:mz_pair_max_distance", params.get("mz_pair_max_distance"))
        params_oms.setValue("superimposer:num_used_points", params.get("num_used_points"))
        params_oms.setValue("pairfinder:distance_MZ:exponent", 3.0)
        params_oms.setValue("pairfinder:distance_RT:exponent", 2.0)

        """
        {b'max_num_peaks_considered': 1000,
        b'superimposer:mz_pair_max_distance': 0.5,
        b'superimposer:rt_pair_distance_fraction': 0.1,
        b'superimposer:num_used_points': 2000,
        b'superimposer:scaling_bucket_size': 0.005,
        b'superimposer:shift_bucket_size': 3.0,
        b'superimposer:max_shift': 1000.0,
        b'superimposer:max_scaling': 2.0,
        b'superimposer:dump_buckets': '',
        b'superimposer:dump_pairs': '',
        b'pairfinder:second_nearest_gap': 2.0,
        b'pairfinder:use_identifications': 'false',
        b'pairfinder:ignore_charge': 'false',
        b'pairfinder:ignore_adduct': 'true',
        b'pairfinder:distance_RT:max_difference': 100.0,
        b'pairfinder:distance_RT:exponent': 1.0,
        b'pairfinder:distance_RT:weight': 1.0,
        b'pairfinder:distance_MZ:max_difference': 0.3,
        b'pairfinder:distance_MZ:unit': 'Da',
        b'pairfinder:distance_MZ:exponent': 2.0,
        b'pairfinder:distance_MZ:weight': 1.0,
        b'pairfinder:distance_intensity:exponent': 1.0,
        b'pairfinder:distance_intensity:weight': 0.0,
        b'pairfinder:distance_intensity:log_transform': 'disabled'}
        """
    elif algo == "kd":
        # Parameters specific to KD algorithm
        params_oms.setValue("mz_unit", "Da")
        params_oms.setValue("nr_partitions", params.get("nr_partitions"))

        # Warp parameters for non-linear RT transformation
        params_oms.setValue("warp:enabled", "true" if params.get("warp_enabled") else "false")
        params_oms.setValue("warp:rt_tol", params.get("warp_rt_tol"))
        params_oms.setValue("warp:mz_tol", params.get("warp_mz_tol"))
        params_oms.setValue("warp:max_pairwise_log_fc", params.get("warp_max_pairwise_log_fc"))
        params_oms.setValue("warp:min_rel_cc_size", params.get("warp_min_rel_cc_size"))
        params_oms.setValue("warp:max_nr_conflicts", params.get("warp_max_nr_conflicts"))

        # Link parameters
        params_oms.setValue("link:rt_tol", params.get("link_rt_tol"))
        params_oms.setValue("link:mz_tol", params.get("link_mz_tol"))
        params_oms.setValue("link:charge_merging", params.get("link_charge_merging"))
        params_oms.setValue("link:adduct_merging", params.get("link_adduct_merging"))

        # Distance parameters
        params_oms.setValue("distance_RT:exponent", params.get("distance_RT_exponent"))
        params_oms.setValue("distance_RT:weight", params.get("distance_RT_weight"))
        params_oms.setValue("distance_MZ:exponent", params.get("distance_MZ_exponent"))
        params_oms.setValue("distance_MZ:weight", params.get("distance_MZ_weight"))
        params_oms.setValue("distance_intensity:exponent", params.get("distance_intensity_exponent"))
        params_oms.setValue("distance_intensity:weight", params.get("distance_intensity_weight"))
        params_oms.setValue("distance_intensity:log_transform", params.get("distance_intensity_log_transform"))

        # LOWESS parameters
        params_oms.setValue("LOWESS:span", params.get("LOWESS_span"))
        params_oms.setValue("LOWESS:num_iterations", params.get("LOWESS_num_iterations"))
        params_oms.setValue("LOWESS:delta", params.get("LOWESS_delta"))
        params_oms.setValue("LOWESS:interpolation_type", params.get("LOWESS_interpolation_type"))
        params_oms.setValue("LOWESS:extrapolation_type", params.get("LOWESS_extrapolation_type"))

    if algo == "pc":
        aligner = oms.MapAlignmentAlgorithmPoseClustering()
        self.logger.info("Starting alignment with PoseClustering")
        # set ref_index to feature map index with largest number of features
        ref_index = [i[0] for i in sorted(enumerate([fm.size() for fm in fmaps]), key=lambda x: x[1])][-1]
        self.logger.debug(
            f"Reference map is {self.samples_df.row(ref_index, named=True)['sample_name']}",
        )
        aligner.setParameters(params_oms)
        aligner.setReference(fmaps[ref_index])
        self.logger.debug(f"Parameters for alignment: {params}")
        # perform alignment and transformation of feature maps to the reference map (exclude reference map)
        tdqm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]
        for index, fm in tqdm(
            list(enumerate(fmaps)),
            total=len(fmaps),
            desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Align feature maps",
            disable=tdqm_disable,
        ):
            if index == ref_index:
                continue
            if params.get("skip_blanks") and self.samples_df.row(index, named=True)["sample_type"] == "blank":
                continue
            trafo = oms.TransformationDescription()
            aligner.align(fm, trafo)
            transformer = oms.MapAlignmentTransformer()
            transformer.transformRetentionTimes(fm, trafo, True)

        self.alignment_ref_index = ref_index

    elif algo == "kd":
        # KD algorithm requires num_maps and Param parameters
        num_maps = len(fmaps)
        aligner = oms.MapAlignmentAlgorithmKD(3, params_oms)
        self.logger.info(f"Starting alignment with KD algorithm using {num_maps} maps")

        kdtree = oms.KDTreeFeatureMaps()
        kdtree.addMaps(fmaps)  # Add all feature maps to the KDTree
        # kdtree.optimizeTree()
        aligner.addRTFitData(kdtree)
        aligner.fitLOWESS()
        aligner.transform(kdtree)

    else:
        self.logger.error(f"Unknown alignment algorithm '{algo}'")

    # check if rt_original exists in features_df, if not, add it after rt
    if "rt_original" not in self.features_df.columns:
        # add column 'rt_original' after 'rt'
        rt_index = self.features_df.columns.get_loc("rt") + 1
        self.features_df.insert(rt_index, "rt_original", 0)
        self.features_df["rt_original"] = self.features_df["rt"]

    # iterate through all feature_maps and add the transformed retention times to the features_df

    # Build a fast lookup for (sample_uid, featureUid) to index in features_df
    feats = self.features_df

    # Pre-build sample_uid lookup for faster access
    self.logger.debug("Build sample_uid lookup for fast access...")
    sample_uid_lookup = {
        idx: row_dict["sample_uid"] for idx, row_dict in enumerate(self.samples_df.iter_rows(named=True))
    }

    # Build the main lookup using feature_uid (not feature_id)
    if "feature_id" in feats.columns:
        # Create lookup mapping (sample_uid, feature_id) to DataFrame index using Polars
        # Since we need a pandas-style index lookup, we'll create a simple dict
        sample_uids = feats.get_column("sample_uid").to_list()

        # Handle feature_id column - it might be Object type due to conversion
        feature_id_col = feats.get_column("feature_id")
        if feature_id_col.dtype == pl.Object:
            # If it's Object type, convert to list and let Python handle the conversion
            feature_ids = feature_id_col.to_list()
            # Convert to strings if they're not already
            feature_ids = [str(fid) if fid is not None else None for fid in feature_ids]
        else:
            # Safe to cast normally
            feature_ids = feature_id_col.cast(pl.Utf8).to_list()

        lookup = {
            (sample_uid, feature_id): idx
            for idx, (sample_uid, feature_id) in enumerate(
                zip(sample_uids, feature_ids, strict=True),
            )
        }
    else:
        # fallback: skip if feature_uid column missing
        lookup = {}
        self.logger.warning("feature_id column not found in features_df")

    # Pre-allocate update lists for better performance
    all_update_idx = []
    all_update_rt = []
    all_update_rt_original = []

    tdqm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]

    for index, fm in tqdm(
        list(enumerate(fmaps)),
        total=len(fmaps),
        desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Extract RTs",
        disable=tdqm_disable,
    ):
        sample_uid = sample_uid_lookup.get(index)
        if sample_uid is None:
            continue

        # Collect all updates for this feature map
        for f in fm:
            feature_uid = str(f.getUniqueId())
            idx = lookup.get((sample_uid, feature_uid))
            if idx is not None:
                rt = round(f.getRT(), 3)
                # rt_or = round(f.getMetaValue("original_RT"), 3) if f.metaValueExists("original_RT") else rt
                all_update_idx.append(idx)
                all_update_rt.append(rt)
                # all_update_rt_original.append(rt_or)

    # Single batch update for all features at once
    if all_update_idx:
        # Build a full-length Python list of rt values, update specified indices,
        # then replace the DataFrame column with a Series that has the same length
        try:
            current_rt = self.features_df["rt"].to_list()
        except Exception:
            current_rt = [None] * self.features_df.height

        # Defensive: ensure list length equals dataframe height
        if len(current_rt) != self.features_df.height:
            current_rt = [None] * self.features_df.height

        for idx, new_rt in zip(all_update_idx, all_update_rt):
            current_rt[idx] = new_rt

        new_cols = [pl.Series("rt", current_rt)]

        # Update rt_original if corresponding updates were collected
        if 'all_update_rt_original' in locals() and all_update_rt_original:
            try:
                current_rt_orig = self.features_df["rt_original"].to_list() if "rt_original" in self.features_df.columns else [None] * self.features_df.height
            except Exception:
                current_rt_orig = [None] * self.features_df.height

            if len(current_rt_orig) != self.features_df.height:
                current_rt_orig = [None] * self.features_df.height

            for idx, new_orig in zip(all_update_idx, all_update_rt_original):
                current_rt_orig[idx] = new_orig

            new_cols.append(pl.Series("rt_original", current_rt_orig))

        # Replace columns in one call
        self.features_df = self.features_df.with_columns(*new_cols)

    self.logger.debug("Alignment completed successfully.")

    if params.get("save_features"):
        self.save_samples()


def merge(self, **kwargs):
    """Group features across samples into consensus features.

    Parameters can be provided as a ``merge_defaults`` instance or as
    individual keyword arguments; they are validated against the defaults class.

    Key parameters (from ``merge_defaults``):
        - algorithm (str): Grouping algorithm to use ('qt', 'kd', 'unlabeled', 'sequential').
        - min_samples (int): Minimum number of samples required for a consensus feature.
        - link_ms2 (bool): Whether to attach/link MS2 spectra to consensus features.
        - mz_tol (float): m/z tolerance for grouping (Da).
        - rt_tol (float): RT tolerance for grouping (seconds).
    """
    # Reset consensus-related DataFrames at the start
    self.consensus_df = pl.DataFrame()
    self.consensus_ms2 = pl.DataFrame()
    self.consensus_mapping_df = pl.DataFrame()

    self.logger.info("Merging...")
    # parameters initialization
    params = merge_defaults()
    for key, value in kwargs.items():
        if isinstance(value, merge_defaults):
            params = value
            self.logger.debug("Using provided merge_defaults parameters")
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
    self.store_history(["merge"], params.to_dict())
    self.logger.debug("Parameters stored to merge")

    # Get parameter values for use in the method
    algorithm = params.get("algorithm")
    min_samples = params.get("min_samples")
    link_ms2 = params.get("link_ms2")
    mz_tol = kwargs.get("mz_tol", 0.01)  # Default values for parameters not in defaults class
    rt_tol = kwargs.get("rt_tol", 1.0)

    if len(self.samples_df) > 200 and algorithm == "qt":
        self.logger.warning(
            "Using QT for large datasets is NOT recommended [O(n²)], consider using KDTree instead [O(n log n)].",
        )

    # check that features_maps is not empty
    if not self.features_maps or len(self.features_maps) == 0:
        self.load_features()
    params_oms = oms.Param()
    ## TODO expose these

    feature_grouper: object  # Use generic type for different OpenMS algorithms
    match algorithm.lower():
        case "kd":
            feature_grouper = oms.FeatureGroupingAlgorithmKD()
            self.logger.debug("Merging features with KDTree...")
            params_oms.setValue("mz_unit", "Da")
            params_oms.setValue("nr_partitions", len(self.samples_df))

            params_oms.setValue("warp:enabled", "true")
            params_oms.setValue("warp:rt_tol", rt_tol)
            params_oms.setValue("warp:mz_tol", mz_tol)

            params_oms.setValue("link:rt_tol", rt_tol)
            params_oms.setValue("link:mz_tol", mz_tol)
        case "unlabeled":
            feature_grouper = oms.FeatureGroupingAlgorithmUnlabeled()
            self.logger.debug("Merging features with Unlabelled algorithm...")
            params_oms.setValue("second_nearest_gap", 2.0)
            params_oms.setValue("ignore_charge", "true")
            params_oms.setValue("distance_RT:max_difference", rt_tol * 3)
            params_oms.setValue("distance_MZ:max_difference", mz_tol * 3)
            params_oms.setValue("distance_MZ:unit", "Da")
        case "sequential":
            self.logger.debug(
                "Merging features sequentially with Unlabelled algorithm...",
            )
            params_oms.setValue("second_nearest_gap", 2.0)
            params_oms.setValue("ignore_charge", "true")
            params_oms.setValue("distance_RT:max_difference", rt_tol * 3)
            params_oms.setValue("distance_MZ:max_difference", mz_tol * 3)
            params_oms.setValue("distance_MZ:unit", "Da")
        case "qt":
            feature_grouper = oms.FeatureGroupingAlgorithmQT()
            self.logger.debug("Grouping features with QT...")
            params_oms.setValue("nr_partitions", len(self.samples_df))
            params_oms.setValue("ignore_charge", "true")
            params_oms.setValue("distance_RT:max_difference", rt_tol * 3)
            params_oms.setValue("distance_MZ:max_difference", mz_tol * 3)
            params_oms.setValue("distance_MZ:unit", "Da")
    self.logger.debug(f"Parameters for feature grouping: {params_oms}")
    consensus_map = oms.ConsensusMap()
    file_descriptions = consensus_map.getColumnHeaders()  # type: ignore
    feature_maps = self.features_maps
    for i, feature_map in enumerate(feature_maps):
        file_description = file_descriptions.get(i, oms.ColumnHeader())
        file_description.filename = self.samples_df.row(i, named=True)["sample_name"]
        file_description.size = feature_map.size()
        file_description.unique_id = feature_map.getUniqueId()
        file_descriptions[i] = file_description

    consensus_map.setColumnHeaders(file_descriptions)  # type: ignore

    # create a copy of the feature maps to store the original feature map information
    match algorithm.lower():
        case "sequential":
            # set the reference map to self.alignment_ref_index
            if self.alignment_ref_index is None:
                # pick the feature map with the most features as reference
                self.alignment_ref_index = max(
                    range(len(self.features_maps)),
                    key=lambda i: self.features_maps[i].size(),
                )
            feature_grouper = oms.FeatureGroupingAlgorithmUnlabeled()
            feature_grouper.setParameters(params_oms)
            feature_grouper.setReference(
                self.alignment_ref_index,
                self.features_maps[self.alignment_ref_index],
            )
            self.logger.info(
                f"Using feature map {self.samples_df.row(self.alignment_ref_index, named=True)['sample_name']} as reference.",
            )

            tdqm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]
            for i, feature_map in tqdm(
                enumerate(self.features_maps),
                total=len(self.features_maps),
                desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Add samples",
                disable=tdqm_disable,
            ):
                if i == self.alignment_ref_index:
                    continue
                feature_grouper.addToGroup(i, feature_map)
            self.logger.debug("Grouping features.")
            consensus_map = feature_grouper.getResultMap()
            if hasattr(consensus_map, "setUniqueIds"):
                consensus_map.setUniqueIds()
        case _:
            feature_grouper.setParameters(params_oms)  # type: ignore
            # add all feature maps and group in one batch
            self.logger.debug("Grouping features in one batch...")
            feature_grouper.group(feature_maps, consensus_map)  # type: ignore
            if hasattr(consensus_map, "setUniqueIds"):
                consensus_map.setUniqueIds()

    # create a dict to map uid to feature_uid using self.features_df
    feature_uid_map = {row["feature_id"]: row["feature_uid"] for row in self.features_df.iter_rows(named=True)}
    imax = consensus_map.size()

    # Pre-build fast lookup tables for features_df data
    features_lookup = {}
    feature_columns = [
        "rt",
        "mz",
        "rt_start",
        "rt_end",
        "rt_delta",
        "mz_start",
        "mz_end",
        "inty",
        "chrom_coherence",
        "chrom_prominence",
        "chrom_prominence_scaled",
        "chrom_height_scaled",
        "iso",
        "charge",
        "ms2_scans",
        "adduct",
        "adduct_mass",
    ]

    for row in self.features_df.iter_rows(named=True):
        feature_uid = row["feature_uid"]
        features_lookup[feature_uid] = {col: row[col] for col in feature_columns if col in self.features_df.columns}

    # create a list to store the consensus mapping
    consensus_mapping = []
    metadata_list = []

    tqdm_disable = self.log_level not in ["TRACE", "DEBUG"]

    for i, feature in enumerate(
        tqdm(
            consensus_map,
            total=imax,
            disable=tqdm_disable,
            desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Extract metadata",
        ),
    ):
        # get all features in the feature map with the same unique id as the consensus feature
        features_list = feature.getFeatureList()
        uids = []
        feature_data_list = []

        for _j, f in enumerate(features_list):
            fuid = str(f.getUniqueId())
            if fuid not in feature_uid_map:
                # this is a feature that was removed but is still in the feature maps
                continue
            fuid = feature_uid_map[fuid]
            consensus_mapping.append({
                "consensus_uid": i,
                "sample_uid": f.getMapIndex() + 1,
                "feature_uid": fuid,
            })
            uids.append(fuid)

            # Get feature data from lookup instead of DataFrame filtering
            feature_data = features_lookup.get(fuid)
            if feature_data:
                feature_data_list.append(feature_data)

        if not feature_data_list:
            # Skip this consensus feature if no valid features found
            continue

        # Compute statistics using vectorized operations on collected data
        # Convert to numpy arrays for faster computation
        rt_values = np.array([fd.get("rt", 0) for fd in feature_data_list if fd.get("rt") is not None])
        mz_values = np.array([fd.get("mz", 0) for fd in feature_data_list if fd.get("mz") is not None])
        rt_start_values = np.array([
            fd.get("rt_start", 0) for fd in feature_data_list if fd.get("rt_start") is not None
        ])
        rt_end_values = np.array([fd.get("rt_end", 0) for fd in feature_data_list if fd.get("rt_end") is not None])
        rt_delta_values = np.array([
            fd.get("rt_delta", 0) for fd in feature_data_list if fd.get("rt_delta") is not None
        ])
        mz_start_values = np.array([
            fd.get("mz_start", 0) for fd in feature_data_list if fd.get("mz_start") is not None
        ])
        mz_end_values = np.array([fd.get("mz_end", 0) for fd in feature_data_list if fd.get("mz_end") is not None])
        inty_values = np.array([fd.get("inty", 0) for fd in feature_data_list if fd.get("inty") is not None])
        coherence_values = np.array([
            fd.get("chrom_coherence", 0) for fd in feature_data_list if fd.get("chrom_coherence") is not None
        ])
        prominence_values = np.array([
            fd.get("chrom_prominence", 0) for fd in feature_data_list if fd.get("chrom_prominence") is not None
        ])
        prominence_scaled_values = np.array([
            fd.get("chrom_prominence_scaled", 0)
            for fd in feature_data_list
            if fd.get("chrom_prominence_scaled") is not None
        ])
        height_scaled_values = np.array([
            fd.get("chrom_height_scaled", 0) for fd in feature_data_list if fd.get("chrom_height_scaled") is not None
        ])
        iso_values = np.array([fd.get("iso", 0) for fd in feature_data_list if fd.get("iso") is not None])
        charge_values = np.array([fd.get("charge", 0) for fd in feature_data_list if fd.get("charge") is not None])

        # adduct_values
        # Collect all adducts from feature_data_list to create consensus adduct information
        all_adducts = []
        adduct_masses = {}

        for fd in feature_data_list:
            # Get individual adduct and mass from each feature data (fd)
            adduct = fd.get("adduct")
            adduct_mass = fd.get("adduct_mass")

            if adduct is not None:
                all_adducts.append(adduct)
                if adduct_mass is not None:
                    adduct_masses[adduct] = adduct_mass

        # Calculate adduct_values for the consensus feature
        adduct_values = []
        if all_adducts:
            adduct_counts = {adduct: all_adducts.count(adduct) for adduct in set(all_adducts)}
            total_count = sum(adduct_counts.values())
            for adduct, count in adduct_counts.items():
                percentage = (count / total_count) * 100 if total_count > 0 else 0
                mass = adduct_masses.get(adduct, None)
                # Store as dict instead of tuple to avoid type confusion
                adduct_values.append({
                    "adduct": str(adduct),
                    "count": int(count),
                    "percentage": float(round(percentage, 2)),
                    "mass": float(mass) if mass is not None else None,
                })

        # Sort adduct_values by count in descending order
        adduct_values.sort(key=lambda x: x["count"], reverse=True)  # type: ignore[arg-type,return-value]
        # Store adduct_values for use in metadata
        consensus_adduct_values = adduct_values

        # Calculate number of MS2 spectra
        ms2_count = 0
        for fd in feature_data_list:
            ms2_scans = fd.get("ms2_scans")
            if ms2_scans is not None:
                ms2_count += len(ms2_scans)

        metadata_list.append({
            "consensus_uid": int(i),  # "consensus_id": i,
            "consensus_id": str(feature.getUniqueId()),
            "quality": round(float(feature.getQuality()), 3),
            "number_samples": len(feature_data_list),
            # "number_ext": int(len(features_list)),
            "rt": round(float(np.mean(rt_values)), 4) if len(rt_values) > 0 else 0.0,
            "mz": round(float(np.mean(mz_values)), 4) if len(mz_values) > 0 else 0.0,
            "rt_min": round(float(np.min(rt_values)), 3) if len(rt_values) > 0 else 0.0,
            "rt_max": round(float(np.max(rt_values)), 3) if len(rt_values) > 0 else 0.0,
            "rt_mean": round(float(np.mean(rt_values)), 3) if len(rt_values) > 0 else 0.0,
            "rt_start_mean": round(float(np.mean(rt_start_values)), 3) if len(rt_start_values) > 0 else 0.0,
            "rt_end_mean": round(float(np.mean(rt_end_values)), 3) if len(rt_end_values) > 0 else 0.0,
            "rt_delta_mean": round(float(np.ptp(rt_delta_values)), 3) if len(rt_delta_values) > 0 else 0.0,
            "mz_min": round(float(np.min(mz_values)), 4) if len(mz_values) > 0 else 0.0,
            "mz_max": round(float(np.max(mz_values)), 4) if len(mz_values) > 0 else 0.0,
            "mz_mean": round(float(np.mean(mz_values)), 4) if len(mz_values) > 0 else 0.0,
            "mz_start_mean": round(float(np.mean(mz_start_values)), 4) if len(mz_start_values) > 0 else 0.0,
            "mz_end_mean": round(float(np.mean(mz_end_values)), 4) if len(mz_end_values) > 0 else 0.0,
            "inty_mean": round(float(np.mean(inty_values)), 0) if len(inty_values) > 0 else 0.0,
            "bl": -1.0,
            "chrom_coherence_mean": round(float(np.mean(coherence_values)), 3) if len(coherence_values) > 0 else 0.0,
            "chrom_prominence_mean": round(float(np.mean(prominence_values)), 0) if len(prominence_values) > 0 else 0.0,
            "chrom_prominence_scaled_mean": round(
                float(np.mean(prominence_scaled_values)),
                3,
            )
            if len(prominence_scaled_values) > 0
            else 0.0,
            "chrom_height_scaled_mean": round(float(np.mean(height_scaled_values)), 3)
            if len(height_scaled_values) > 0
            else 0.0,
            "iso_mean": round(float(np.mean(iso_values)), 2) if len(iso_values) > 0 else 0.0,
            "charge_mean": round(float(np.mean(charge_values)), 2) if len(charge_values) > 0 else 0.0,
            "number_ms2": int(ms2_count),
            "adducts": consensus_adduct_values if consensus_adduct_values else [],  # Ensure it's always a list
        })

    consensus_mapping_df = pl.DataFrame(consensus_mapping)
    # remove all rows in consensus_mapping_df where consensus_id is not in self.featured_df['uid']
    l1 = len(consensus_mapping_df)
    consensus_mapping_df = consensus_mapping_df.filter(
        pl.col("feature_uid").is_in(self.features_df["feature_uid"].to_list()),
    )
    self.logger.debug(
        f"Filtered {l1 - len(consensus_mapping_df)} orphan features from maps.",
    )
    self.consensus_mapping_df = consensus_mapping_df
    self.consensus_df = pl.DataFrame(metadata_list, strict=False)

    if min_samples is None:
        min_samples = 1
    if min_samples < 1:
        min_samples = int(min_samples * len(self.samples_df))
    
    # Validate that min_samples doesn't exceed the number of samples
    if min_samples > len(self.samples_df):
        self.logger.warning(
            f"min_samples ({min_samples}) exceeds the number of samples ({len(self.samples_df)}). "
            f"Setting min_samples to {len(self.samples_df)}."
        )
        min_samples = len(self.samples_df)
    
    # filter out consensus features with less than min_samples features
    l1 = len(self.consensus_df)
    self.consensus_df = self.consensus_df.filter(
        pl.col("number_samples") >= min_samples,
    )
    self.logger.debug(
        f"Filtered {l1 - len(self.consensus_df)} consensus features with less than {min_samples} samples.",
    )
    # filter out consensus mapping with less than min_samples features
    self.consensus_mapping_df = self.consensus_mapping_df.filter(
        pl.col("consensus_uid").is_in(self.consensus_df["consensus_uid"].to_list()),
    )

    self.consensus_map = consensus_map
    # calculate the completeness of the consensus map
    c = len(self.consensus_mapping_df) / len(self.consensus_df) / len(self.samples_df)
    self.logger.info(
        f"Merging completed. Consensus features: {len(self.consensus_df)}. Completeness: {c:.2f}.",
    )
    if link_ms2:
        self.find_ms2()


# Backward compatibility alias
find_consensus = merge


def find_ms2(self, **kwargs):
    """
    Links MS2 spectra to consensus features and stores the result in self.consensus_ms2.

    Parameters:
        **kwargs: Keyword arguments for MS2 linking parameters. Can include:
            - A find_ms2_defaults instance to set all parameters at once
            - Individual parameter names and values (see find_ms2_defaults for details)
    """
    # Reset consensus_ms2 DataFrame at the start
    self.consensus_ms2 = pl.DataFrame()

    # parameters initialization
    params = find_ms2_defaults()
    for key, value in kwargs.items():
        if isinstance(value, find_ms2_defaults):
            params = value
            self.logger.debug("Using provided find_ms2_defaults parameters")
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
    self.store_history(["find_ms2"], params.to_dict())
    self.logger.debug("Parameters stored to find_ms2")

    data = []
    if self.consensus_mapping_df.is_empty():
        self.logger.error(
            "No consensus mapping found. Please run merge() first.",
        )
        return
    self.logger.info("Linking MS2 spectra to consensus features...")

    # Build fast lookup for feature_uid to features_df row data
    feats = self.features_df
    feature_lookup = {}
    relevant_cols = [
        "ms2_specs",
        "ms2_scans",
        "inty",
        "chrom_coherence",
        "chrom_prominence_scaled",
    ]
    for row in feats.iter_rows(named=True):
        feature_uid = row["feature_uid"]
        feature_lookup[feature_uid] = {col: row[col] for col in relevant_cols if col in feats.columns}
    tdqm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]

    # Process consensus mapping in batch
    for mapping_row in tqdm(
        self.consensus_mapping_df.iter_rows(named=True),
        total=self.consensus_mapping_df.shape[0],
        desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}MS2 spectra",
        disable=tdqm_disable,
    ):
        feature_uid = mapping_row["feature_uid"]
        feature_data = feature_lookup.get(feature_uid)
        if feature_data is None or feature_data.get("ms2_specs") is None:
            continue
        ms2_specs = feature_data["ms2_specs"]
        ms2_scans = feature_data["ms2_scans"]
        inty = feature_data.get("inty")
        chrom_coherence = feature_data.get("chrom_coherence")
        chrom_prominence_scaled = feature_data.get("chrom_prominence_scaled")
        for j in range(len(ms2_specs)):
            spec = ms2_specs[j]
            scanid = ms2_scans[j]
            data.append({
                "consensus_uid": int(mapping_row["consensus_uid"]),
                "feature_uid": int(mapping_row["feature_uid"]),
                "sample_uid": int(mapping_row["sample_uid"]),
                "scan_id": int(scanid),
                "energy": round(spec.energy, 1) if hasattr(spec, "energy") and spec.energy is not None else None,
                "prec_inty": round(inty, 0) if inty is not None else None,
                "prec_coherence": round(chrom_coherence, 3) if chrom_coherence is not None else None,
                "prec_prominence_scaled": round(chrom_prominence_scaled, 3)
                if chrom_prominence_scaled is not None
                else None,
                "number_frags": len(spec.mz),
                "spec": spec,
            })
    self.consensus_ms2 = pl.DataFrame(data)
    if not self.consensus_ms2.is_empty():
        unique_consensus_features = self.consensus_ms2["consensus_uid"].n_unique()
    else:
        unique_consensus_features = 0
    self.logger.info(
        f"Linking completed. {len(self.consensus_ms2)} MS2 spectra associated to {unique_consensus_features} consensus features.",
    )


## TODO these are not modelled the same way as other ranges, harmonize for tuples
def filter_consensus(
    self,
    inplace=True,
    number_samples=None,
    quality=None,
    coherence=None,
):
    if self.consensus_df is None:
        self.logger.error("No consensus found.")
        return
    cons = self.consensus_df if inplace else self.consensus_df.copy()
    l = len(cons)
    self.logger.info(f"Filtering consensus features with {l} entries...")
    if coherence is not None:
        if "chrom_coherence" not in cons.columns:
            self.logger.warning("No coherence data found in features.")
        else:
            if isinstance(coherence, tuple) and len(coherence) == 2:
                min_coherence, max_coherence = coherence
                cons = cons[(cons["chrom_coherence"] >= min_coherence) & (cons["chrom_coherence"] <= max_coherence)]
            else:
                cons = cons[cons["chrom_coherence"] >= coherence]
        l2 = len(cons)
        self.logger.info(
            f"Filtered {l - l2} entries based on coherence. Remaining {l2} entries.",
        )

    if quality is not None:
        if isinstance(quality, tuple) and len(quality) == 2:
            min_quality, max_quality = quality
            cons = cons[(cons["quality"] >= min_quality) & (cons["quality"] <= max_quality)]
        else:
            cons = cons[cons["quality"] >= quality]
        l3 = len(cons)
        self.logger.info(
            f"Filtered {l2 - l3} entries based on quality. Remaining {l3} entries.",
        )

    if number_samples is not None:
        if isinstance(number_samples, tuple) and len(number_samples) == 2:
            min_number, max_number = number_samples
            cons = cons[(cons["number_samples"] >= min_number) & (cons["number_samples"] <= max_number)]
        else:
            cons = cons[cons["number_samples"] >= number_samples]
        l4 = len(cons)
        self.logger.info(
            f"Filtered {l3 - l4} entries based on number of samples. Remaining {l4} entries.",
        )

    self.logger.info(f"Filtering completed. {len(cons)} entries remaining.")

    if inplace:
        self.consensus_df = cons
    else:
        return cons


## TODO is uid supposed to be a list? rt_tol 0?
def _integrate_chrom_impl(self, **kwargs):
    """Integrate chromatogram intensities for consensus features.

    Integrates EICs for consensus features using parameters defined in
    :class:`integrate_defaults`. Pass an ``integrate_defaults`` instance via
    ``**kwargs`` or override individual parameters (they will be validated
    against the defaults class).

    Main parameters (from ``integrate_defaults``):

    - uids (Optional[list]): List of consensus UIDs to integrate; ``None`` means all.
    - rt_tol (float): RT tolerance (seconds) used when locating integration boundaries.

    Notes:
        This function batches updates to the study's feature table for efficiency.
    """
    # parameters initialization
    params = integrate_defaults()
    for key, value in kwargs.items():
        if isinstance(value, integrate_defaults):
            params = value
            self.logger.debug("Using provided integrate_chrom_defaults parameters")
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
    self.store_history(["integrate_chrom"], params.to_dict())
    self.logger.debug("Parameters stored to integrate_chrom")

    # Get parameter values for use in the method
    uids = params.get("uids")
    rt_tol = params.get("rt_tol")

    if self.consensus_map is None:
        self.logger.error("No consensus map found.")
        return
    if uids is None:
        # get all consensus_id from consensus_df
        ids = self.consensus_df["consensus_uid"].to_list()
    else:
        # keep only id that are in consensus_df
        ids = [i for i in uids if i in self.consensus_df["consensus_uid"].to_list()]

    # Ensure chrom_area column is Float64 to avoid dtype conflicts
    if "chrom_area" in self.features_df.columns:
        self.features_df = self.features_df.with_columns(
            pl.col("chrom_area").cast(pl.Float64, strict=False),
        )

    # Merge consensus_mapping with consensus_df to get rt_start_mean and rt_end_mean
    # Use Polars join operation instead of pandas merge
    consensus_subset = self.consensus_df.select([
        "consensus_uid",
        "rt_start_mean",
        "rt_end_mean",
    ])
    df1 = self.consensus_mapping_df.join(
        consensus_subset,
        on="consensus_uid",
        how="left",
    )
    df1 = df1.filter(pl.col("consensus_uid").is_in(ids))

    # Build a fast lookup for feature_uid to row index in features_df
    # Since Polars doesn't have index-based access like pandas, we'll use row position
    feature_uid_to_row = {}
    for i, row_dict in enumerate(self.features_df.iter_rows(named=True)):
        if "feature_uid" in row_dict:
            feature_uid_to_row[row_dict["feature_uid"]] = i
        elif "uid" in row_dict:  # fallback column name
            feature_uid_to_row[row_dict["uid"]] = i

    # Prepare lists for batch update
    update_rows = []
    chroms: list = []
    rt_starts: list[float] = []
    rt_ends: list[float] = []
    rt_deltas: list[float] = []
    chrom_areas = []

    self.logger.debug(f"Integrating {df1.shape[0]} features using consensus...")
    tdqm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]
    for row in tqdm(
        df1.iter_rows(named=True),
        total=df1.shape[0],
        desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Integrate EICs by consensus",
        disable=tdqm_disable,
    ):
        feature_uid = row["feature_uid"]
        row_idx = feature_uid_to_row.get(feature_uid)
        if row_idx is None:
            continue

        # Get the feature row from Polars DataFrame
        feature_row = self.features_df.row(row_idx, named=True)
        # get chromatogram for the feature
        chrom = feature_row["chrom"]
        if chrom is None or len(chrom) == 0:
            update_rows.append(row_idx)
            chroms.append(None)
            rt_starts.append(None)
            rt_ends.append(None)
            rt_deltas.append(None)
            chrom_areas.append(-1.0)
            continue
        ## TODO expose parameters
        rt_start = _find_closest_valley(
            chrom,
            row["rt_start_mean"] - rt_tol,
            dir="left",
            threshold=0.9,
        )
        rt_end = _find_closest_valley(
            chrom,
            row["rt_end_mean"] + rt_tol,
            dir="right",
            threshold=0.9,
        )
        chrom.feature_start = rt_start
        chrom.feature_end = rt_end
        chrom.integrate()
        update_rows.append(row_idx)
        chroms.append(chrom)
        rt_starts.append(rt_start)
        rt_ends.append(rt_end)
        rt_deltas.append(rt_end - rt_start)
        chrom_areas.append(float(chrom.feature_area))

    # Batch update DataFrame - Polars style
    if update_rows:
        # Create mapping from row index to new values
        row_to_chrom = {update_rows[i]: chroms[i] for i in range(len(update_rows))}
        row_to_rt_start = {update_rows[i]: rt_starts[i] for i in range(len(update_rows))}
        row_to_rt_end = {update_rows[i]: rt_ends[i] for i in range(len(update_rows))}
        row_to_rt_delta = {update_rows[i]: rt_deltas[i] for i in range(len(update_rows))}
        row_to_chrom_area = {
            update_rows[i]: float(chrom_areas[i]) if chrom_areas[i] is not None else 0.0
            for i in range(len(update_rows))
        }

        # Use with_row_index to create a temporary row index column
        df_with_index = self.features_df.with_row_index("__row_idx")

        # Create update masks and values
        update_mask = pl.col("__row_idx").is_in(update_rows)

        # Update columns conditionally
        try:
            self.features_df = df_with_index.with_columns([
                # Update chrom column - use when() to update only specific rows
                pl.when(update_mask)
                .then(
                    pl.col("__row_idx").map_elements(
                        lambda x: row_to_chrom.get(x, None),
                        return_dtype=pl.Object,
                    ),
                )
                .otherwise(pl.col("chrom"))
                .alias("chrom"),
                # Update rt_start column
                pl.when(update_mask)
                .then(
                    pl.col("__row_idx").map_elements(
                        lambda x: row_to_rt_start.get(x, None),
                        return_dtype=pl.Float64,
                    ),
                )
                .otherwise(pl.col("rt_start"))
                .alias("rt_start"),
                # Update rt_end column
                pl.when(update_mask)
                .then(
                    pl.col("__row_idx").map_elements(
                        lambda x: row_to_rt_end.get(x, None),
                        return_dtype=pl.Float64,
                    ),
                )
                .otherwise(pl.col("rt_end"))
                .alias("rt_end"),
                # Update rt_delta column
                pl.when(update_mask)
                .then(
                    pl.col("__row_idx").map_elements(
                        lambda x: row_to_rt_delta.get(x, None),
                        return_dtype=pl.Float64,
                    ),
                )
                .otherwise(pl.col("rt_delta"))
                .alias("rt_delta"),
                # Update chrom_area column
                pl.when(update_mask)
                .then(
                    pl.col("__row_idx").map_elements(
                        lambda x: row_to_chrom_area.get(x, 0),
                        return_dtype=pl.Float64,
                    ),
                )
                .otherwise(pl.col("chrom_area"))
                .alias("chrom_area"),
            ]).drop("__row_idx")  # Remove the temporary row index column

            self.logger.debug(
                f"Integration completed. Updated {len(update_rows)} features with chromatogram data.",
            )
        except Exception as e:
            self.logger.error(f"Failed to update features DataFrame: {e}")
    else:
        self.logger.debug("No features were updated during integration.")


def integrate(self, **kwargs):
    """Integrate chromatograms across consensus features.

    Wrapper that extracts parameters from :class:`integrate_defaults` and
    calls the underlying implementation. See ``integrate_defaults`` for
    the canonical parameter list and descriptions.
    """
    # parameters initialization
    params = integrate_defaults()
    for key, value in kwargs.items():
        if isinstance(value, integrate_defaults):
            params = value
            self.logger.debug("Using provided integrate_defaults parameters")
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
    self.store_history(["integrate"], params.to_dict())
    self.logger.debug("Parameters stored to integrate")

    # Call the original integrate_chrom function with extracted parameters
    return _integrate_chrom_impl(
        self,
        uids=params.get("uids"),
        rt_tol=params.get("rt_tol"),
    )


# Backward compatibility alias
integrate_chrom = integrate


def _find_closest_valley(chrom, rt, dir="left", threshold=0.9):
    # find closest index to rt in chrom['rt']
    chrom.rt = chrom.rt.astype(np.float64)
    chrom.inty = chrom.inty.astype(np.float64)
    idx = np.abs(chrom.rt - rt).argmin()
    # ensure rt and inty are float64
    if dir == "left":
        inty = np.inf
        # iterate left from idx to the end od the peaks until we find a valley
        for i in range(idx, 0, -1):
            if chrom.inty[i] < inty * threshold:
                idx = i
                inty = chrom.inty[i]
            else:
                break
    if dir == "right":
        inty = np.inf
        # iterate right from idx to the end od the peaks until we find a valley
        for i in range(idx, len(chrom.inty)):
            if chrom.inty[i] < inty * threshold:
                idx = i
                inty = chrom.inty[i]
            else:
                break
    return chrom.rt[idx]
