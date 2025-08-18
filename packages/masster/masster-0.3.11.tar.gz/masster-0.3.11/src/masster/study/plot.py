from __future__ import annotations

from datetime import datetime
from typing import Any

import holoviews as hv
import numpy as np
import panel
import polars as pl
from tqdm import tqdm

hv.extension("bokeh")


def plot_alignment(self, filename=None):
    import matplotlib.pyplot as plt
    import numpy as np

    if self.features_maps is None or len(self.features_maps) == 0:
        self.load_features()

    feature_maps = self.features_maps
    ref_index = self.alignment_ref_index
    if ref_index is None:
        self.logger.error("No alignment performed yet.")
        return

    fmaps = [
        feature_maps[ref_index],
        *feature_maps[:ref_index],
        *feature_maps[ref_index + 1 :],
    ]

    fig = plt.figure(figsize=(12, 6))

    ax = fig.add_subplot(1, 2, 1)
    ax.set_title("Feature maps before alignment")
    ax.set_ylabel("m/z")
    ax.set_xlabel("RT")

    # use alpha value to display feature intensity
    ax.scatter(
        [f.getRT() for f in fmaps[0]],
        [f.getMZ() for f in fmaps[0]],
        alpha=np.asarray([f.getIntensity() for f in fmaps[0]]) / max([f.getIntensity() for f in fmaps[0]]),
        s=4,
    )

    for fm in fmaps[1:]:
        ax.scatter(
            [f.getMetaValue("original_RT") for f in fm],
            [f.getMZ() for f in fm],
            alpha=np.asarray([f.getIntensity() for f in fm]) / max([f.getIntensity() for f in fm]),
            s=2,  # Set symbol size to 3
        )

    ax = fig.add_subplot(1, 2, 2)
    ax.set_title("Feature maps after alignment")
    ax.set_ylabel("m/z")
    ax.set_xlabel("RT")

    for fm in fmaps:
        ax.scatter(
            [f.getRT() for f in fm],
            [f.getMZ() for f in fm],
            alpha=np.asarray([f.getIntensity() for f in fm]) / max([f.getIntensity() for f in fm]),
            s=2,  # Set symbol size to 3
        )

    fig.tight_layout()


def plot_alignment_bokeh(self, filename=None):
    from bokeh.plotting import figure, show, output_file
    from bokeh.layouts import gridplot

    feature_maps = self.features_maps
    ref_index = self.alignment_ref_index
    if ref_index is None:
        self.logger.warning("No alignment performed yet.")
        return

    fmaps = [
        feature_maps[ref_index],
        *feature_maps[:ref_index],
        *feature_maps[ref_index + 1 :],
    ]

    # Create Bokeh figures
    p1 = figure(
        title="Feature maps before alignment",
        width=600,
        height=400,
    )
    p1.xaxis.axis_label = "RT"
    p1.yaxis.axis_label = "m/z"
    p2 = figure(
        title="Feature maps after alignment",
        width=600,
        height=400,
    )
    p2.xaxis.axis_label = "RT"
    p2.yaxis.axis_label = "m/z"

    # Plot before alignment
    p1.scatter(
        x=[f.getRT() for f in fmaps[0]],
        y=[f.getMZ() for f in fmaps[0]],
        size=4,
        alpha=[f.getIntensity() / max([f.getIntensity() for f in fmaps[0]]) for f in fmaps[0]],
        color="blue",
    )

    for fm in fmaps[1:]:
        p1.scatter(
            x=[f.getMetaValue("original_RT") for f in fm],
            y=[f.getMZ() for f in fm],
            size=2,
            alpha=[f.getIntensity() / max([f.getIntensity() for f in fm]) for f in fm],
            color="green",
        )

    # Plot after alignment
    for fm in fmaps:
        p2.scatter(
            x=[f.getRT() for f in fm],
            y=[f.getMZ() for f in fm],
            size=2,
            alpha=[f.getIntensity() / max([f.getIntensity() for f in fm]) for f in fm],
            color="red",
        )

    # Arrange plots in a grid
    # Link the x_range and y_range of both plots for synchronized zooming/panning
    p2.x_range = p1.x_range
    p2.y_range = p1.y_range

    grid = gridplot([[p1, p2]])

    # Output to file and show
    if filename:
        output_file(filename)
    show(grid)


def plot_consensus_2d(
    self,
    filename=None,
    colorby="number_samples",
    sizeby="inty_mean",
    markersize=6,
    size="dynamic",
    alpha=0.7,
    cmap=None,
    width=900,
    height=900,
    mz_range=None,
    rt_range=None,
):
    """
    Plot consensus features in a 2D scatter plot with retention time vs m/z.

    Parameters:
        filename (str, optional): Path to save the plot
        colorby (str): Column name to use for color mapping (default: "number_samples")
        sizeby (str): Column name to use for size mapping (default: "inty_mean")
        markersize (int): Base marker size (default: 6)
        size (str): Controls whether points scale with zoom. Options:
                   'dynamic' - points use circle() and scale with zoom
                   'static' - points use scatter() and maintain fixed pixel size
        alpha (float): Transparency level (default: 0.7)
        cmap (str, optional): Color map name
        width (int): Plot width in pixels (default: 900)
        height (int): Plot height in pixels (default: 900)
        mz_range (tuple, optional): m/z range for filtering consensus features (min_mz, max_mz)
        rt_range (tuple, optional): Retention time range for filtering consensus features (min_rt, max_rt)
    """
    if self.consensus_df is None:
        self.logger.error("No consensus map found.")
        return
    data = self.consensus_df.clone()

    # Filter by mz_range and rt_range if provided
    if mz_range is not None:
        data = data.filter((pl.col("mz") >= mz_range[0]) & (pl.col("mz") <= mz_range[1]))
    if rt_range is not None:
        data = data.filter((pl.col("rt") >= rt_range[0]) & (pl.col("rt") <= rt_range[1]))

    if colorby not in data.columns:
        self.logger.error(f"Column {colorby} not found in consensus_df.")
        return
    if sizeby not in data.columns:
        self.logger.warning(f"Column {sizeby} not found in consensus_df.")
        sizeby = None
    # if sizeby is not None, set markersize to sizeby
    if sizeby is not None:
        # set markersize to sizeby
        if sizeby in ["inty_mean"]:
            # use log10 of sizeby
            # Filter out empty or all-NA entries before applying np.log10
            data = data.with_columns([
                pl.when(
                    (pl.col(sizeby).is_not_null()) & (pl.col(sizeby).is_finite()) & (pl.col(sizeby) > 0),
                )
                .then((pl.col(sizeby).log10() * markersize / 12).pow(2))
                .otherwise(markersize)
                .alias("markersize"),
            ])
        else:
            max_size = data[sizeby].max()
            data = data.with_columns([
                (pl.col(sizeby) / max_size * markersize).alias("markersize"),
            ])
    else:
        data = data.with_columns([pl.lit(markersize).alias("markersize")])
    # sort by ascending colorby
    data = data.sort(colorby)
    # convert consensus_id to string - check if column exists
    if "consensus_id" in data.columns:
        # Handle Object dtype by converting to string first
        data = data.with_columns([
            pl.col("consensus_id")
            .map_elements(
                lambda x: str(x) if x is not None else None,
                return_dtype=pl.Utf8,
            )
            .alias("consensus_id"),
        ])
    elif "consensus_uid" in data.columns:
        data = data.with_columns([
            pl.col("consensus_uid").cast(pl.Utf8).alias("consensus_id"),
        ])

    if cmap is None:
        cmap = "vi"
    elif cmap == "grey":
        cmap = "Greys256"

    # plot with bokeh
    import bokeh.plotting as bp

    from bokeh.models import BasicTicker
    from bokeh.models import ColumnDataSource
    from bokeh.models import HoverTool
    from bokeh.models import LinearColorMapper

    try:
        from bokeh.models import ColorBar  # type: ignore[attr-defined]
    except ImportError:
        from bokeh.models.annotations import ColorBar
    from bokeh.palettes import viridis

    # Convert Polars DataFrame to pandas for Bokeh compatibility
    data_pd = data.to_pandas()
    source = ColumnDataSource(data_pd)
    color_mapper = LinearColorMapper(
        palette=viridis(256),
        low=data[colorby].min(),
        high=data[colorby].max(),
    )
    # scatter plot rt vs mz
    p = bp.figure(
        width=width,
        height=height,
        title="Consensus map",
    )
    p.xaxis.axis_label = "Retention Time (min)"
    p.yaxis.axis_label = "m/z"
    scatter_renderer: Any = None
    if size.lower() in ["dyn", "dynamic"]:
        scatter_renderer = p.circle(
            x="rt",
            y="mz",
            radius=markersize / 10,
            fill_color={"field": colorby, "transform": color_mapper},
            line_color=None,
            alpha=alpha,
            source=source,
        )
    else:
        scatter_renderer = p.scatter(
            x="rt",
            y="mz",
            size="markersize",
            fill_color={"field": colorby, "transform": color_mapper},
            line_color=None,
            alpha=alpha,
            source=source,
        )
    # add hover tool
    hover = HoverTool(
        tooltips=[
            ("consensus_uid", "@consensus_uid"),
            ("consensus_id", "@consensus_id"),
            ("number_samples", "@number_samples"),
            ("number_ms2", "@number_ms2"),
            ("rt", "@rt"),
            ("mz", "@mz"),
            ("inty_mean", "@inty_mean"),
            ("iso_mean", "@iso_mean"),
            ("coherence_mean", "@chrom_coherence_mean"),
            ("prominence_mean", "@chrom_prominence_mean"),
        ],
        renderers=[scatter_renderer],
    )
    p.add_tools(hover)

    # add colorbar
    color_bar = ColorBar(
        color_mapper=color_mapper,
        label_standoff=12,
        location=(0, 0),
        title=colorby,
        ticker=BasicTicker(desired_num_ticks=8),
    )
    p.add_layout(color_bar, "right")

    if filename is not None:
        bp.output_file(filename)
    bp.show(p)
    return p


def plot_samples_2d(
    self,
    samples=None,
    filename=None,
    markersize=2,
    size="dynamic",
    alpha_max=0.8,
    alpha="inty",
    cmap="Turbo256",
    max_features=50000,
    width=900,
    height=900,
    mz_range=None,
    rt_range=None,
):
    """
    Plot all feature maps for sample_uid in parameter uids in an overlaid scatter plot.
    Each sample is a different color. Alpha scales with intensity.
    OPTIMIZED VERSION: Uses vectorized operations and batch processing.

    Parameters:
        samples: Sample UIDs to plot
        filename (str, optional): Path to save the plot
        markersize (int): Base marker size (default: 2)
        size (str): Controls whether points scale with zoom. Options:
                   'dynamic' or 'dyn' - points use circle() and scale with zoom
                   'const', 'static' or other - points use scatter() and maintain fixed pixel size
        alpha_max (float): Maximum transparency level (default: 0.8)
        alpha (str): Column name to use for alpha mapping (default: "inty")
        cmap (str): Color map name (default: "Turbo256")
        max_features (int): Maximum number of features to plot (default: 50000)
        width (int): Plot width in pixels (default: 900)
        height (int): Plot height in pixels (default: 900)
        mz_range (tuple, optional): m/z range for filtering features (min_mz, max_mz)
        rt_range (tuple, optional): Retention time range for filtering features (min_rt, max_rt)
    """

    # Local bokeh imports to avoid heavy top-level dependency
    from bokeh.plotting import figure, show, output_file
    from bokeh.io.export import export_png
    from bokeh.models import ColumnDataSource, HoverTool
    from bokeh.palettes import Turbo256

    sample_uids = self._get_sample_uids(samples)

    if not sample_uids:
        self.logger.error("No valid sample_uids provided.")
        return

    colors = Turbo256
    color_map = {uid: colors[i * (256 // max(1, len(sample_uids)))] for i, uid in enumerate(sample_uids)}

    p = figure(
        width=width,
        height=height,
        title="Sample Features",
    )
    p.xaxis.axis_label = "Retention Time (RT)"
    p.yaxis.axis_label = "m/z"

    # OPTIMIZATION 1: Batch filter all features for selected samples at once
    features_batch = self.features_df.filter(pl.col("sample_uid").is_in(sample_uids))

    # Filter by mz_range and rt_range if provided
    if mz_range is not None:
        features_batch = features_batch.filter((pl.col("mz") >= mz_range[0]) & (pl.col("mz") <= mz_range[1]))
    if rt_range is not None:
        features_batch = features_batch.filter((pl.col("rt") >= rt_range[0]) & (pl.col("rt") <= rt_range[1]))

    if features_batch.is_empty():
        self.logger.error("No features found for the selected samples.")
        return

    # OPTIMIZATION 8: Fast sampling for very large datasets to maintain interactivity
    max_features_per_plot = max_features  # Limit for interactive performance
    total_features = len(features_batch)

    if total_features > max_features_per_plot:
        # OPTIMIZED: Much faster random sampling without groupby operations
        sample_ratio = max_features_per_plot / total_features
        self.logger.info(
            f"Large dataset detected ({total_features:,} features). "
            f"Sampling {sample_ratio:.1%} for visualization performance.",
        )

        # FAST: Use simple random sampling instead of expensive stratified sampling
        n_samples = min(max_features_per_plot, total_features)
        features_batch = features_batch.sample(n=n_samples, seed=42)

    # OPTIMIZATION 2: Join with samples_df to get sample names in one operation
    samples_info = self.samples_df.filter(pl.col("sample_uid").is_in(sample_uids))
    features_with_names = features_batch.join(
        samples_info.select(["sample_uid", "sample_name"]),
        on="sample_uid",
        how="left",
    )

    # OPTIMIZATION 4: Fast pre-calculation of alpha values for all features
    if alpha == "inty":
        # OPTIMIZED: Use efficient Polars operations instead of pandas groupby transform
        # Calculate max intensity per sample in Polars (much faster)
        max_inty_per_sample = features_with_names.group_by("sample_uid").agg(
            pl.col("inty").max().alias("max_inty"),
        )

        # Join back and calculate alpha efficiently
        features_batch = (
            features_with_names.join(
                max_inty_per_sample,
                on="sample_uid",
                how="left",
            )
            .with_columns(
                (pl.col("inty") / pl.col("max_inty") * alpha_max).alias("alpha"),
            )
            .drop("max_inty")
        )

        # Convert to pandas once after all Polars operations
        features_pd = features_batch.to_pandas()
    else:
        # Convert to pandas and add constant alpha
        features_pd = features_with_names.to_pandas()
        features_pd["alpha"] = alpha_max

    # OPTIMIZATION 9: NEW - Batch create all ColumnDataSources at once
    # Group all data by sample_uid and create sources efficiently
    sources = {}
    renderers: list[Any] = []

    # Pre-compute color mapping to avoid repeated lookups
    color_values = {}
    sample_names = {}

    for uid in sample_uids:
        sample_data = features_pd[features_pd["sample_uid"] == uid]
        if sample_data.empty:
            continue

        sample_name = sample_data["sample_name"].iloc[0]
        sample_names[uid] = sample_name
        color_values[uid] = color_map[uid]

    # OPTIMIZATION 10: Batch renderer creation with pre-computed values
    for uid in sample_uids:
        sample_data = features_pd[features_pd["sample_uid"] == uid]
        if sample_data.empty:
            continue

        sample_name = sample_names[uid]
        color_values[uid]

        # OPTIMIZATION 11: Direct numpy array access for better performance
        source = ColumnDataSource(
            data={
                "rt": sample_data["rt"].values,
                "mz": sample_data["mz"].values,
                "inty": sample_data["inty"].values,
                "alpha": sample_data["alpha"].values,
                "sample": np.full(len(sample_data), sample_name, dtype=object),
            },
        )

        sources[uid] = source

        # OPTIMIZATION 12: Use pre-computed color value
        # Create renderer with pre-computed values
        renderer: Any
        if size.lower() in ["dyn", "dynamic"]:
            renderer = p.circle(
                x="rt",
                y="mz",
                radius=markersize / 10,
                color=color_values[uid],
                alpha="alpha",
                legend_label=sample_name,
                source=source,
            )
        else:
            renderer = p.scatter(
                x="rt",
                y="mz",
                size=markersize,
                color=color_values[uid],
                alpha="alpha",
                legend_label=sample_name,
                source=source,
            )
        renderers.append(renderer)

    # OPTIMIZATION 13: Simplified hover tool for better performance with many samples
    if renderers:
        hover = HoverTool(
            tooltips=[
                ("sample", "@sample"),
                ("rt", "@rt{0.00}"),
                ("mz", "@mz{0.0000}"),
                ("intensity", "@inty{0.0e+0}"),
            ],
            renderers=renderers,
        )
        p.add_tools(hover)

    # Remove legend from plot
    p.legend.visible = False
    if filename:
        if filename.endswith(".html"):
            output_file(filename)
            show(p)
        elif filename.endswith(".png"):
            export_png(p, filename=filename)
        else:
            output_file(filename)
            show(p)
    else:
        show(p)
    return


def plot_chrom(
    self,
    uids=None,
    samples=None,
    filename=None,
    aligned=True,
    width=800,
    height=300,
):
    cons_uids = self._get_consensus_uids(uids)
    sample_uids = self._get_sample_uids(samples)

    chroms = self.get_chrom(uids=cons_uids, samples=sample_uids)

    if chroms is None or chroms.is_empty():
        self.logger.error("No chromatogram data found.")
        return

    # Local import for color palette
    from bokeh.palettes import Turbo256

    # Assign a fixed color to each sample/column
    sample_names = [col for col in chroms.columns if col not in ["consensus_uid"]]
    if not sample_names:
        self.logger.error("No sample names found in chromatogram data.")
        return
    color_map = {sample: Turbo256[i * (256 // max(1, len(sample_names)))] for i, sample in enumerate(sample_names)}

    plots = []
    self.logger.info(f"Plotting {chroms.shape[0]} chromatograms...")
    tqdm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]
    for row in tqdm(
        chroms.iter_rows(named=True),
        total=chroms.shape[0],
        desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Plot chromatograms",
        disable=tqdm_disable,
    ):
        consensus_uid = row["consensus_uid"]  # Get consensus_uid from the row
        consensus_id = consensus_uid  # Use the same value for consensus_id
        curves = []
        rt_min = np.inf
        rt_max = 0
        for sample in sample_names:
            chrom = row[sample]
            if chrom is not None:
                # check if chrom is nan
                if isinstance(chrom, float) and np.isnan(chrom):
                    continue

                chrom = chrom.to_dict()
                rt = chrom["rt"].copy()
                if len(rt) == 0:
                    continue
                if aligned and "rt_shift" in chrom:
                    rt_shift = chrom["rt_shift"]
                    if rt_shift is not None:
                        # Convert to numpy array if it's a list, then add scalar
                        if isinstance(rt, list):
                            rt = np.array(rt)
                        rt = rt + rt_shift  # Add scalar to array

                # update rt_min and rt_max
                if rt[0] < rt_min:
                    rt_min = rt[0]
                if rt[-1] > rt_max:
                    rt_max = rt[-1]

                inty = chrom["inty"]

                # Convert both rt and inty to numpy arrays if they're lists
                if isinstance(rt, list):
                    rt = np.array(rt)
                if isinstance(inty, list):
                    inty = np.array(inty)

                # Ensure both rt and inty are arrays and have the same length and are not empty
                if rt.size > 0 and inty.size > 0 and rt.shape == inty.shape:
                    # sort rt and inty by rt
                    sorted_indices = np.argsort(rt)
                    rt = rt[sorted_indices]
                    inty = inty[sorted_indices]
                    curve = hv.Curve((rt, inty), kdims=["RT"], vdims=["inty"]).opts(
                        color=color_map[sample],
                        line_width=1,
                    )
                    curves.append(curve)

                    if "feature_start" in chrom and "feature_end" in chrom:
                        # Add vertical lines for feature start and end
                        feature_start = chrom["feature_start"]
                        feature_end = chrom["feature_end"]
                        if aligned and "rt_shift" in chrom:
                            rt_shift = chrom["rt_shift"]
                            if rt_shift is not None:
                                feature_start += rt_shift
                                feature_end += rt_shift
                        if feature_start < rt_min:
                            rt_min = feature_start
                        if feature_end > rt_max:
                            rt_max = feature_end
                        # Add vertical lines to the curves
                        curves.append(
                            hv.VLine(feature_start).opts(
                                color=color_map[sample],
                                line_dash="dotted",
                                line_width=1,
                            ),
                        )
                        curves.append(
                            hv.VLine(feature_end).opts(
                                color=color_map[sample],
                                line_dash="dotted",
                                line_width=1,
                            ),
                        )
        if curves:
            # find row in consensus_df with consensus_id
            consensus_row = self.consensus_df.filter(
                pl.col("consensus_uid") == consensus_id,
            )
            rt_start_mean = consensus_row["rt_start_mean"][0]
            rt_end_mean = consensus_row["rt_end_mean"][0]
            # Add vertical lines to overlay
            curves.append(hv.VLine(rt_start_mean).opts(color="black", line_width=2))
            curves.append(hv.VLine(rt_end_mean).opts(color="black", line_width=2))

            overlay = hv.Overlay(curves).opts(
                height=height,
                width=width,
                title=f"Consensus UID: {consensus_id}, mz: {consensus_row['mz'][0]:.4f}, rt: {consensus_row['rt'][0]:.2f}{' (aligned)' if aligned else ''}",
                xlim=(rt_min, rt_max),
                shared_axes=False,
            )
            plots.append(overlay)

    if not plots:
        self.logger.warning("No valid chromatogram curves to plot.")
        return

    # stack vertically.
    # Stack all plots vertically in a Panel column
    layout = panel.Column(*[panel.panel(plot) for plot in plots])
    if filename is not None:
        if filename.endswith(".html"):
            panel.panel(layout).save(filename, embed=True)  # type: ignore[attr-defined]
        else:
            # Save as PNG using Panel's export_png if filename ends with .png
            if filename.endswith(".png"):
                from panel.io.save import save_png

                # Convert Holoviews overlays to Bokeh models before saving
                bokeh_layout = panel.panel(layout).get_root()  # type: ignore[attr-defined]
                save_png(bokeh_layout, filename=filename)
            else:
                panel.panel(layout).save(filename, embed=True)  # type: ignore[attr-defined]
    else:
        # In a server context, return the panel object instead of showing or saving directly
        # return panel.panel(layout)
        panel.panel(layout).show()


def plot_consensus_stats(
    self,
    filename=None,
    width=1200,
    height=1200,
    alpha=0.6,
    markersize=3,
):
    """
    Plot a scatter plot matrix (SPLOM) of consensus statistics using Bokeh.

    Parameters:
        filename (str, optional): Output filename for saving the plot
        width (int): Overall width of the plot (default: 1200)
        height (int): Overall height of the plot (default: 1200)
        alpha (float): Point transparency (default: 0.6)
        markersize (int): Size of points (default: 5)
    """
    from bokeh.layouts import gridplot
    from bokeh.models import ColumnDataSource, HoverTool
    from bokeh.plotting import figure, show, output_file

    # Check if consensus_df exists and has data
    if self.consensus_df is None or self.consensus_df.is_empty():
        self.logger.error("No consensus data available. Run merge/find_consensus first.")
        return

    # Define the columns to plot
    columns = [
        "rt",
        "mz",
        "number_samples",
        "log10_quality",
        "mz_delta_mean",
        "rt_delta_mean",
        "chrom_coherence_mean",
        "chrom_prominence_scaled_mean",
        "inty_mean",
        "number_ms2",
    ]

    # Check which columns exist in the dataframe and compute missing ones
    available_columns = self.consensus_df.columns
    data_df = self.consensus_df.clone()

    # Add log10_quality if quality exists
    if "quality" in available_columns and "log10_quality" not in available_columns:
        data_df = data_df.with_columns(
            pl.col("quality").log10().alias("log10_quality"),
        )

    # Filter columns that actually exist
    final_columns = [col for col in columns if col in data_df.columns]

    if len(final_columns) < 2:
        self.logger.error(f"Need at least 2 columns for SPLOM. Available: {final_columns}")
        return

    self.logger.debug(f"Creating SPLOM with columns: {final_columns}")

    # Add important ID columns for tooltips even if not plotting them
    tooltip_columns = []
    for id_col in ["consensus_uid", "consensus_id"]:
        if id_col in data_df.columns and id_col not in final_columns:
            tooltip_columns.append(id_col)

    # Select plotting columns plus tooltip columns
    all_columns = final_columns + tooltip_columns
    data_pd = data_df.select(all_columns).to_pandas()

    # Remove any infinite or NaN values
    data_pd = data_pd.replace([np.inf, -np.inf], np.nan).dropna()

    if data_pd.empty:
        self.logger.error("No valid data after removing NaN/infinite values.")
        return

    source = ColumnDataSource(data_pd)

    n_vars = len(final_columns)

    # Fixed dimensions - override user input to ensure consistent layout
    total_width = 1200
    total_height = 1200

    # Calculate plot sizes to ensure uniform inner plot areas
    # First column needs extra width for y-axis labels
    plot_width_first = 180  # Wider to account for y-axis labels
    plot_width_others = 120  # Standard width for other columns
    plot_height_normal = 120  # Standard height
    plot_height_last = 155  # Taller last row to accommodate x-axis labels while keeping inner plot area same size

    # Create grid of plots with variable outer sizes but equal inner areas
    plots = []

    for i, y_var in enumerate(final_columns):
        row = []
        for j, x_var in enumerate(final_columns):
            # Determine if this plot needs axis labels
            has_x_label = i == n_vars - 1  # bottom row
            has_y_label = j == 0  # left column

            # First column wider to accommodate y-axis labels, ensuring equal inner plot areas
            current_width = plot_width_first if has_y_label else plot_width_others
            current_height = plot_height_last if has_x_label else plot_height_normal

            p = figure(
                width=current_width,
                height=current_height,
                title=None,  # No title on any plot
                toolbar_location=None,
                # Adjusted borders - first column has more space, others minimal
                min_border_left=70 if has_y_label else 15,
                min_border_bottom=50 if has_x_label else 15,
                min_border_right=15,
                min_border_top=15,
            )

            # Ensure subplot background and border are explicitly white so the plot looks
            # correct in dark and light themes.
            p.outline_line_color = None
            p.border_fill_color = "white"
            p.border_fill_alpha = 1.0
            p.background_fill_color = "white"

            # Remove axis lines to eliminate black lines between plots
            p.xaxis.axis_line_color = None
            p.yaxis.axis_line_color = None

            # Keep subtle grid lines for data reference
            p.grid.visible = True
            p.grid.grid_line_color = "#E0E0E0"  # Light gray grid lines

            # Set axis labels and formatting
            if has_x_label:  # bottom row
                p.xaxis.axis_label = x_var
                p.xaxis.axis_label_text_font_size = "12pt"
                p.xaxis.major_label_text_font_size = "9pt"
                p.xaxis.axis_label_standoff = 15
            else:
                p.xaxis.major_label_text_font_size = "0pt"
                p.xaxis.minor_tick_line_color = None
                p.xaxis.major_tick_line_color = None

            if has_y_label:  # left column
                p.yaxis.axis_label = y_var
                p.yaxis.axis_label_text_font_size = "10pt"  # Smaller y-axis title
                p.yaxis.major_label_text_font_size = "8pt"
                p.yaxis.axis_label_standoff = 12
            else:
                p.yaxis.major_label_text_font_size = "0pt"
                p.yaxis.minor_tick_line_color = None
                p.yaxis.major_tick_line_color = None

            if i == j:
                # Diagonal: histogram
                hist, edges = np.histogram(data_pd[x_var], bins=30)
                p.quad(
                    top=hist,
                    bottom=0,
                    left=edges[:-1],
                    right=edges[1:],
                    fill_color="green",
                    line_color="white",
                    alpha=alpha,
                )
            else:
                # Off-diagonal: scatter plot
                scatter = p.scatter(
                    x=x_var,
                    y=y_var,
                    size=markersize,
                    alpha=alpha,
                    color="blue",
                    source=source,
                )

                # Add hover tool
                hover = HoverTool(
                    tooltips=[
                        (x_var, f"@{x_var}{{0.0000}}"),
                        (y_var, f"@{y_var}{{0.0000}}"),
                        (
                            "consensus_uid",
                            "@consensus_uid"
                            if "consensus_uid" in data_pd.columns
                            else "@consensus_id"
                            if "consensus_id" in data_pd.columns
                            else "N/A",
                        ),
                        ("rt", "@rt{0.00}" if "rt" in data_pd.columns else "N/A"),
                        ("mz", "@mz{0.0000}" if "mz" in data_pd.columns else "N/A"),
                    ],
                    renderers=[scatter],
                )
                p.add_tools(hover)

            row.append(p)
        plots.append(row)

    # Link axes for same variables
    for i in range(n_vars):
        for j in range(n_vars):
            if i != j:  # Don't link diagonal plots
                # Link x-axis to other plots in same column
                for k in range(n_vars):
                    if k != i and k != j:
                        plots[i][j].x_range = plots[k][j].x_range

                # Link y-axis to other plots in same row
                for k in range(n_vars):
                    if k != j and k != i:
                        plots[i][j].y_range = plots[i][k].y_range

    # Create grid layout and force overall background/border to white so the outer
    # container doesn't show dark UI colors in night mode.
    grid = gridplot(plots)

    # Set overall background and border to white when supported
    if hasattr(grid, "background_fill_color"):
        grid.background_fill_color = "white"
    if hasattr(grid, "border_fill_color"):
        grid.border_fill_color = "white"

    # Output and show
    if filename:
        output_file(filename)

    show(grid)
    return grid


def plot_pca(
    self,
    filename=None,
    width=600,
    height=600,
    alpha=0.8,
    markersize=8,
    n_components=2,
    color_by=None,
    title="PCA of Consensus Matrix",
):
    """
    Plot PCA (Principal Component Analysis) of the consensus matrix using Bokeh.

    Parameters:
        filename (str, optional): Output filename for saving the plot
        width (int): Plot width (default: 800)
        height (int): Plot height (default: 600)
        alpha (float): Point transparency (default: 0.8)
        markersize (int): Size of points (default: 8)
        n_components (int): Number of PCA components to compute (default: 2)
        color_by (str, optional): Column from samples_df to color points by
        title (str): Plot title (default: "PCA of Consensus Matrix")
    """
    from bokeh.models import ColumnDataSource, HoverTool, ColorBar, LinearColorMapper
    from bokeh.plotting import figure, show, output_file
    from bokeh.palettes import Category20, viridis
    from bokeh.transform import factor_cmap
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
    import pandas as pd
    import numpy as np

    # Check if consensus matrix and samples_df exist
    try:
        consensus_matrix = self.get_consensus_matrix()
        samples_df = self.samples_df
    except Exception as e:
        self.logger.error(f"Error getting consensus matrix or samples_df: {e}")
        return

    if consensus_matrix is None or consensus_matrix.shape[0] == 0:
        self.logger.error("No consensus matrix available. Run merge/find_consensus first.")
        return

    if samples_df is None or samples_df.is_empty():
        self.logger.error("No samples dataframe available.")
        return

    self.logger.info(f"Performing PCA on consensus matrix with shape: {consensus_matrix.shape}")

    # Convert consensus matrix to numpy if it's not already
    if hasattr(consensus_matrix, "values"):
        matrix_data = consensus_matrix.values
    elif hasattr(consensus_matrix, "to_numpy"):
        matrix_data = consensus_matrix.to_numpy()
    else:
        matrix_data = np.array(consensus_matrix)

    # Transpose matrix so samples are rows and features are columns
    matrix_data = matrix_data.T

    # Handle missing values by replacing with 0
    matrix_data = np.nan_to_num(matrix_data, nan=0.0, posinf=0.0, neginf=0.0)

    # Standardize the data
    scaler = StandardScaler()
    matrix_scaled = scaler.fit_transform(matrix_data)

    # Perform PCA
    pca = PCA(n_components=n_components)
    pca_result = pca.fit_transform(matrix_scaled)

    # Get explained variance ratios
    explained_var = pca.explained_variance_ratio_

    self.logger.info(f"PCA explained variance ratios: {explained_var}")

    # Convert samples_df to pandas for easier manipulation
    samples_pd = samples_df.to_pandas()

    # Create dataframe with PCA results and sample information
    pca_df = pd.DataFrame({
        "PC1": pca_result[:, 0],
        "PC2": pca_result[:, 1] if n_components > 1 else np.zeros(len(pca_result)),
    })

    # Add sample information to PCA dataframe
    if len(samples_pd) == len(pca_df):
        for col in samples_pd.columns:
            pca_df[col] = samples_pd[col].values
    else:
        self.logger.warning(
            f"Sample count mismatch: samples_df has {len(samples_pd)} rows, "
            f"but consensus matrix has {len(pca_df)} samples"
        )

    # Prepare color mapping
    color_column = None
    color_mapper = None

    if color_by and color_by in pca_df.columns:
        color_column = color_by
        unique_values = pca_df[color_by].unique()

        # Handle categorical vs numeric coloring
        if pca_df[color_by].dtype in ["object", "string", "category"]:
            # Categorical coloring
            if len(unique_values) <= 20:
                palette = Category20[min(20, max(3, len(unique_values)))]
            else:
                palette = viridis(min(256, len(unique_values)))
            color_mapper = factor_cmap(color_by, palette, unique_values)
        else:
            # Numeric coloring
            palette = viridis(256)
            color_mapper = LinearColorMapper(
                palette=palette,
                low=pca_df[color_by].min(),
                high=pca_df[color_by].max(),
            )

    # Create Bokeh plot
    p = figure(
        width=width,
        height=height,
        title=f"{title} (PC1: {explained_var[0]:.1%}, PC2: {explained_var[1]:.1%})",
        tools="pan,wheel_zoom,box_zoom,reset,save",
    )

    p.xaxis.axis_label = f"PC1 ({explained_var[0]:.1%} variance)"
    p.yaxis.axis_label = f"PC2 ({explained_var[1]:.1%} variance)"

    # Create data source
    source = ColumnDataSource(pca_df)

    # Create scatter plot
    if color_mapper:
        if isinstance(color_mapper, LinearColorMapper):
            scatter = p.scatter(
                "PC1",
                "PC2",
                size=markersize,
                alpha=alpha,
                color={"field": color_by, "transform": color_mapper},
                source=source,
            )
            # Add colorbar for numeric coloring
            color_bar = ColorBar(color_mapper=color_mapper, width=8, location=(0, 0))
            p.add_layout(color_bar, "right")
        else:
            scatter = p.scatter(
                "PC1",
                "PC2",
                size=markersize,
                alpha=alpha,
                color=color_mapper,
                source=source,
                legend_field=color_by,
            )
    else:
        scatter = p.scatter(
            "PC1",
            "PC2",
            size=markersize,
            alpha=alpha,
            color="blue",
            source=source,
        )

    # Create comprehensive hover tooltips with all sample information
    tooltip_list = [
        ("PC1", "@PC1{0.00}"),
        ("PC2", "@PC2{0.00}"),
    ]

    # Add all sample dataframe columns to tooltips
    for col in samples_pd.columns:
        if col in pca_df.columns:
            if pca_df[col].dtype in ["float64", "float32"]:
                tooltip_list.append((col, f"@{col}{{0.00}}"))
            else:
                tooltip_list.append((col, f"@{col}"))

    hover = HoverTool(
        tooltips=tooltip_list,
        renderers=[scatter],
    )
    p.add_tools(hover)

    # Add legend if using categorical coloring
    if color_mapper and not isinstance(color_mapper, LinearColorMapper) and color_by:
        p.legend.location = "top_left"
        p.legend.click_policy = "hide"

    # Output and show
    if filename:
        output_file(filename)

    show(p)
    return p
