"""
Optimized features_select method for improved performance.

This module contains the optimized version of features_select that:
1. Combines all filters into a single expression
2. Uses lazy evaluation
3. Reduces logging overhead
4. Pre-checks column existence
5. Implements early returns
"""

import polars as pl


def features_select_optimized(
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
    Optimized version of features_select with improved performance.

    Key optimizations:
    - Combines all filters into a single expression
    - Uses lazy evaluation for better performance
    - Reduces logging overhead
    - Pre-checks column existence once
    - Early return for no filters

    Args:
        mz: mass-to-charge ratio filter (tuple for range, single value for minimum)
        rt: retention time filter (tuple for range, single value for minimum)
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

    # Early return if no filters provided
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

    # Pre-check available columns once
    available_columns = set(self.features_df.columns)

    # Build all filter conditions
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

    # Log warnings once at the end
    for warning in warnings:
        self.logger.warning(warning)

    # Apply all filters at once if any exist
    if filter_conditions:
        # Combine all conditions with AND
        combined_filter = filter_conditions[0]
        for condition in filter_conditions[1:]:
            combined_filter = combined_filter & condition

        # Apply the combined filter using lazy evaluation for better performance
        feats = self.features_df.lazy().filter(combined_filter).collect()
    else:
        feats = self.features_df.clone()

    final_count = len(feats)

    if final_count == 0:
        self.logger.warning("No features remaining after applying selection criteria.")
    else:
        removed_count = initial_count - final_count
        self.logger.info(f"Features selected: {final_count} (removed: {removed_count})")

    return feats


def features_select_benchmarked(
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
    Benchmarked version that compares old vs new implementation performance.
    """
    import time

    # Call the original method for comparison
    start_time = time.perf_counter()
    _ = self.features_select_original(
        mz=mz,
        rt=rt,
        inty=inty,
        sample_uid=sample_uid,
        sample_name=sample_name,
        consensus_uid=consensus_uid,
        feature_uid=feature_uid,
        filled=filled,
        quality=quality,
        chrom_coherence=chrom_coherence,
        chrom_prominence=chrom_prominence,
        chrom_prominence_scaled=chrom_prominence_scaled,
        chrom_height_scaled=chrom_height_scaled,
    )
    original_time = time.perf_counter() - start_time

    # Call the optimized method
    start_time = time.perf_counter()
    result_optimized = features_select_optimized(
        self,
        mz=mz,
        rt=rt,
        inty=inty,
        sample_uid=sample_uid,
        sample_name=sample_name,
        consensus_uid=consensus_uid,
        feature_uid=feature_uid,
        filled=filled,
        quality=quality,
        chrom_coherence=chrom_coherence,
        chrom_prominence=chrom_prominence,
        chrom_prominence_scaled=chrom_prominence_scaled,
        chrom_height_scaled=chrom_height_scaled,
    )
    optimized_time = time.perf_counter() - start_time

    # Log performance comparison
    speedup = original_time / optimized_time if optimized_time > 0 else float("inf")
    self.logger.info(
        f"Performance comparison - Original: {original_time:.4f}s, Optimized: {optimized_time:.4f}s, Speedup: {speedup:.2f}x"
    )

    return result_optimized


def monkey_patch_study():
    """
    Apply the optimized features_select method to the Study class.

    Call this function to replace the original features_select with the optimized version.
    """
    from masster.study.study import Study

    # Store original method for benchmarking
    Study.features_select_original = Study.features_select

    # Replace with optimized version
    Study.features_select = features_select_optimized

    # Add benchmarked version as an option
    Study.features_select_benchmarked = features_select_benchmarked

    print("Successfully patched Study.features_select with optimized version")
