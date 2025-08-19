from __future__ import annotations

import os

from datetime import datetime

import numpy as np
import pandas as pd
import polars as pl

from tqdm import tqdm

from masster.spectrum import combine_peaks
from masster.study.defaults import export_mgf_defaults
from masster._version import get_version


def _get_mgf_df(self, **kwargs):
    """
    Generate MGF data as a Polars DataFrame.

    This is the core data generation function used by export_mgf().

    Parameters:
        **kwargs: Keyword arguments for export parameters. Same as export_mgf()
                 except return_data is not relevant here.

    Returns:
        pl.DataFrame: DataFrame with columns:
            - mgf_index: MGF index
            - title: MGF title string
            - feature_id: Consensus feature ID
            - feature_uid: Consensus feature UID
            - charge: Charge state
            - pepmass: Precursor m/z
            - rtinseconds: Retention time in seconds
            - mslevel: MS level
            - type: Spectrum type (e.g., "MS2")
            - energy: Collision energy (if available)
            - spec_len: Number of peaks in spectrum
            - spec_mz: List of spectrum m/z values
            - spec_int: List of spectrum intensity values
    """
    # parameters initialization
    params = export_mgf_defaults()
    for key, value in kwargs.items():
        if isinstance(value, export_mgf_defaults):
            params = value
            self.logger.debug("Using provided export_defaults parameters")
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
    self.store_history(["get_mgf"], params.to_dict())
    self.logger.debug("Parameters stored to get_mgf")

    # Get parameter values for use in the method
    selection = params.get("selection")
    split_energy = params.get("split_energy")
    merge = params.get("merge")
    mz_start = params.get("mz_start")
    mz_end = params.get("mz_end")
    rt_start = params.get("rt_start")
    rt_end = params.get("rt_end")
    centroid = params.get("centroid")
    inty_min = params.get("inty_min")
    deisotope = params.get("deisotope")

    if self.consensus_df is None:
        self.logger.error("No consensus map found. Please run merge() first.")
        return None
    if self.consensus_ms2 is None:
        self.logger.error("No consensus MS2 data found. Please run link_ms2() first.")
        return None

    # Convert to pandas for merge operation since the result is used for groupby
    consensus_df_pd = self.consensus_df.to_pandas()
    consensus_ms2_pd = self.consensus_ms2.to_pandas()

    features = pd.merge(
        consensus_df_pd,
        consensus_ms2_pd,
        how="right",
        on="consensus_uid",
    )
    if len(features) == 0:
        self.logger.warning("No features found.")
        return pl.DataFrame()

    # Pre-group by consensus_uid for fast access
    grouped = features.groupby("consensus_uid")

    def filter_peaks(spec, inty_min=None):
        spec = spec.copy()
        length = len(spec.mz)
        mask = np.ones(length, dtype=bool)
        if inty_min is not None and inty_min > 0:
            mask = mask & (spec.inty >= inty_min)
        for attr in spec.__dict__:
            arr = getattr(spec, attr)
            if isinstance(arr, list | np.ndarray) and hasattr(arr, "__len__") and len(arr) == length:
                setattr(spec, attr, np.array(arr)[mask])
        return spec

    def create_ion_dict(title, id, uid, mz, rt, charge, spect, mgf_id):
        """Create a dictionary representing an ion for the DataFrame."""
        if spect is None:
            return None

        # Prepare spectrum data
        spectrum_mz = spect.mz.tolist() if hasattr(spect.mz, "tolist") else list(spect.mz)
        spectrum_inty = spect.inty.tolist() if hasattr(spect.inty, "tolist") else list(spect.inty)

        # Determine MS level
        ms_level = spect.ms_level if spect.ms_level is not None else 1

        # Get energy if available
        energy = getattr(spect, "energy", None)

        # Determine spectrum type based on MS level
        spec_type = f"MS{ms_level}" if ms_level > 1 else "MS1"

        # Calculate spectrum length
        spec_len = len(spectrum_mz)

        return {
            "mgf_index": mgf_id,
            "title": title,
            "feature_id": id,
            "feature_uid": uid,
            "charge": charge,
            "pepmass": mz,
            "rtinseconds": rt,
            "mslevel": ms_level,
            "type": spec_type,
            "energy": energy,
            "spec_len": spec_len,
            "spec_mz": spectrum_mz,
            "spec_int": spectrum_inty,
        }

    # Collect all ion data
    ion_data = []
    skip = 0
    mgf_counter = 0
    self.logger.info(f"Generating MGF data for {len(grouped)} consensus features...")

    tdqm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]
    for _consensus_uid, cons_ms2 in tqdm(
        grouped,
        total=len(grouped),
        desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Feature",
        disable=tdqm_disable,
    ):
        # Use the first row for feature-level info
        row = cons_ms2.iloc[0]
        if mz_start is not None and row["mz"] < mz_start:
            continue
        if mz_end is not None and row["mz"] > mz_end:
            continue
        if rt_start is not None and row["rt"] < rt_start:
            continue
        if rt_end is not None and row["rt"] > rt_end:
            continue
        if len(cons_ms2) == 0:
            skip += 1
            continue

        if split_energy:
            energies = cons_ms2["energy"].unique()
            for e in energies:
                cons_ms2_e = cons_ms2[cons_ms2["energy"] == e]
                if selection == "best":
                    idx = cons_ms2_e["prec_inty"].idxmax()
                    cons_ms2_e_row = cons_ms2_e.loc[idx]
                    spect = cons_ms2_e_row["spec"]
                    if spect is None:
                        skip += 1
                        continue
                    if centroid:
                        spect = spect.centroid()
                    if deisotope:
                        spect = spect.deisotope()
                    spect = filter_peaks(spect, inty_min=inty_min)
                    mgf_counter += 1
                    ion_dict = create_ion_dict(
                        f"uid:{cons_ms2_e_row['consensus_uid']}, rt:{cons_ms2_e_row['rt']:.2f}, mz:{cons_ms2_e_row['mz']:.4f}, energy:{e}, sample_uid:{cons_ms2_e_row['sample_uid']}, scan_id:{cons_ms2_e_row['scan_id']}",
                        cons_ms2_e_row["consensus_id"],
                        cons_ms2_e_row["consensus_uid"],
                        cons_ms2_e_row["mz"],
                        cons_ms2_e_row["rt"],
                        round(cons_ms2_e_row["charge_mean"]),
                        spect,
                        mgf_counter,
                    )
                    if ion_dict is not None:
                        ion_data.append(ion_dict)
                else:
                    for row_e in cons_ms2_e.iter_rows(named=True):
                        spect = row_e["spec"]
                        if spect is None:
                            continue
                        if centroid:
                            spect = spect.centroid()
                        if deisotope:
                            spect = spect.deisotope()
                        spect = filter_peaks(spect, inty_min=inty_min)
                        mgf_counter += 1
                        ion_dict = create_ion_dict(
                            f"uid:{row_e['consensus_uid']}, rt:{row_e['rt']:.2f}, mz:{row_e['mz']:.4f}, energy:{e}, sample_uid:{row_e['sample_uid']}, scanid:{row_e['scan_id']}",
                            row_e["consensus_id"],
                            row_e["consensus_uid"],
                            row_e["mz"],
                            row_e["rt"],
                            round(row_e["charge_mean"]),
                            spect,
                            mgf_counter,
                        )
                        if ion_dict is not None:
                            ion_data.append(ion_dict)
        else:
            if selection == "best":
                idx = cons_ms2["prec_inty"].idxmax()
                cons_ms2_e_row = cons_ms2.loc[idx]
                spect = cons_ms2_e_row["spec"]
                if spect is None:
                    continue
                if centroid:
                    spect = spect.centroid()
                if deisotope:
                    spect = spect.deisotope()
                spect = filter_peaks(spect, inty_min=inty_min)
                mgf_counter += 1
                ion_dict = create_ion_dict(
                    f"uid:{cons_ms2_e_row['consensus_uid']}, rt:{cons_ms2_e_row['rt']:.2f}, mz:{cons_ms2_e_row['mz']:.4f}, energy:{cons_ms2_e_row['energy']}, sample_uid:{cons_ms2_e_row['sample_uid']}, scan_id:{cons_ms2_e_row['scan_id']}",
                    cons_ms2_e_row["consensus_id"],
                    cons_ms2_e_row["consensus_uid"],
                    cons_ms2_e_row["mz"],
                    cons_ms2_e_row["rt"],
                    round(cons_ms2_e_row["charge_mean"]),
                    spect,
                    mgf_counter,
                )
                if ion_dict is not None:
                    ion_data.append(ion_dict)

            elif selection == "all":
                if merge:
                    specs = [row_e["spec"] for row_e in cons_ms2.iter_rows(named=True) if row_e["spec"] is not None]
                    if not specs:
                        continue
                    spect = combine_peaks(specs)
                    if centroid:
                        spect = spect.denoise()
                        spect = spect.centroid()
                    if deisotope:
                        spect = spect.deisotope()
                    spect = filter_peaks(spect, inty_min=inty_min)
                    mgf_counter += 1
                    ion_dict = create_ion_dict(
                        f"uid:{row['consensus_uid']}, rt:{row['rt']:.2f}, mz:{row['mz']:.4f}, sample_uid:{row['sample_uid']}, scan_id:{row['scan_id']}",
                        row["consensus_id"],
                        row["consensus_uid"],
                        row["mz"],
                        row["rt"],
                        round(row["charge_mean"]),
                        spect,
                        mgf_counter,
                    )
                    if ion_dict is not None:
                        ion_data.append(ion_dict)
                else:
                    for row_e in cons_ms2.iter_rows(named=True):
                        spect = row_e["spec"]
                        if spect is None:
                            continue
                        if centroid:
                            spect = spect.centroid()
                        if deisotope:
                            spect = spect.deisotope()
                        spect = filter_peaks(spect, inty_min=inty_min)
                        mgf_counter += 1
                        ion_dict = create_ion_dict(
                            f"uid:{row_e['consensus_uid']}, rt:{row_e['rt']:.2f}, mz:{row_e['mz']:.4f}, energy:{row_e['energy']}, sample_uid:{row_e['sample_uid']}, scan_id:{row_e['scan_id']}",
                            row_e["consensus_id"],
                            row_e["consensus_uid"],
                            row_e["mz"],
                            row_e["rt"],
                            round(row_e["charge_mean"]),
                            spect,
                            mgf_counter,
                        )
                        if ion_dict is not None:
                            ion_data.append(ion_dict)

    self.logger.debug(f"Generated MGF data for {len(ion_data)} spectra")
    self.logger.debug(f"Skipped {skip} features due to missing data.")

    # Convert to Polars DataFrame
    if not ion_data:
        return pl.DataFrame()

    return pl.DataFrame(ion_data)


def export_mgf(self, **kwargs):
    """
    Export consensus features as MGF format for database searching.

    Parameters:
        **kwargs: Keyword arguments for export parameters. Can include:
            - An export_defaults instance to set all parameters at once
            - Individual parameter names and values (see export_defaults for details)

    Key Parameters:
        filename (str): Output MGF file name (default: "features.mgf").
        selection (str): "best" for first scan, "all" for every scan (default: "best").
        split_energy (bool): Process MS2 scans by unique energy (default: True).
        merge (bool): If selection="all", merge MS2 scans into one spectrum (default: False).
        mz_start (float): Minimum m/z for feature selection (default: None).
        mz_end (float): Maximum m/z for feature selection (default: None).
        rt_start (float): Minimum RT for feature selection (default: None).
        rt_end (float): Maximum RT for feature selection (default: None).
        centroid (bool): Apply centroiding to spectra (default: True).
        inty_min (float): Minimum intensity threshold (default: None).
        deisotope (bool): Apply deisotoping to spectra (default: True).
        verbose (bool): Enable verbose logging (default: False).
        precursor_trim (float): Precursor trimming value (default: -10).
        centroid_algo (str): Centroiding algorithm (default: "lmp").

    Returns:
        None: Writes MGF file to disk.
    """
    # Get mgf data as DataFrame
    mgf_data = self._get_mgf_df(**kwargs)

    if mgf_data is None or len(mgf_data) == 0:
        self.logger.warning("No MGF data generated.")
        return

    # Get filename from parameters
    params = export_mgf_defaults()
    for key, value in kwargs.items():
        if isinstance(value, export_mgf_defaults):
            params = value
        else:
            if hasattr(params, key):
                params.set(key, value, validate=True)

    filename = params.get("filename")

    # Prepare output path
    if not os.path.isabs(filename):
        if self.folder is not None:
            filename = os.path.join(self.folder, filename)
        else:
            filename = os.path.join(os.getcwd(), filename)

    # Write MGF file
    with open(filename, "w", encoding="utf-8") as f:
        for row in mgf_data.iter_rows(named=True):
            # Write BEGIN IONS
            f.write("BEGIN IONS\n")

            # Write metadata
            if row["mgf_index"] is not None:
                f.write(f"INDEX={row['mgf_index']}\n")
            f.write(f"TITLE={row['title']}\n")
            f.write(f"FEATURE_ID={row['feature_id']}\n")
            f.write(f"FEATURE_UID={row['feature_uid']}\n")
            f.write(f"CHARGE={row['charge']}\n")
            f.write(f"PEPMASS={row['pepmass']}\n")
            f.write(f"RTINSECONDS={row['rtinseconds']}\n")
            f.write(f"MSLEVEL={row['mslevel']}\n")

            if row["energy"] is not None:
                f.write(f"ENERGY={row['energy']}\n")

            # Write spectrum data
            spectrum_mz = row["spec_mz"]
            spectrum_inty = row["spec_int"]
            for mz_val, inty in zip(spectrum_mz, spectrum_inty, strict=False):
                f.write(f"{mz_val:.5f} {inty:.0f}\n")

            # Write END IONS
            f.write("END IONS\n\n")

    self.logger.info(f"Exported {len(mgf_data)} spectra to {filename}")


def export_mztab(self, filename: str = None, include_mgf=True, **kwargs) -> None:
    """
    Export the study as a fully compliant mzTab-M file.

    Args:
        filename (str, optional): Path to the output mzTab-M file.
        title (str, optional): Human-readable title for the file.
        description (str, optional): Human-readable description.
        **kwargs: Additional metadata or export options.
    """
    if filename is None:
        filename = "study.mztab"
    if not os.path.isabs(filename):
        if self.folder is not None:
            filename = os.path.join(self.folder, filename)
        else:
            filename = os.path.join(os.getcwd(), filename)

    # get mgf data
    mgf_data = self._get_mgf_df(**kwargs)
    # Create mapping from feature_uid to MGF indexes
    mgf_mapping: dict[str, list[int]] = {}
    if mgf_data is not None and len(mgf_data) > 0:
        for row in mgf_data.iter_rows(named=True):
            feature_uid = row["feature_uid"]
            mgf_index = row["mgf_index"]
            if feature_uid not in mgf_mapping:
                mgf_mapping[feature_uid] = []
            mgf_mapping[feature_uid].append(mgf_index)

    # --- Prepare MTD (metadata) section ---
    mtd_lines = []
    mtd_lines.append(f"COM file generated by MASSter on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    mtd_lines.append("\nMTD\tmzTab-version\t2.2.0-M")
    id = self.label if self.label else self.folder
    mtd_lines.append(f"MTD\tmzTab-id\t{id}")
    mtd_lines.append("")
    mtd_lines.append("MTD\tcv[1]-label\tMS")
    mtd_lines.append("MTD\tcv[1]-full_name\tPSI-MS controlled vocabulary")
    mtd_lines.append("MTD\tcv[1]-version\t4.1.199")
    mtd_lines.append("MTD\tcv[1]-uri\thttps://raw.githubusercontent.com/HUPO-PSI/psi-ms-CV/master/psi-ms.obo")
    mtd_lines.append("")
    mtd_lines.append("MTD\tsmall_molecule-quantification_unit\t[MS, MS:1001844, MS1 feature area, ]")
    mtd_lines.append("MTD\tsmall_molecule_feature-quantification_unit\t[MS, MS:1001844, MS1 feature area, ]")
    mtd_lines.append(
        "MTD\tsmall_molecule-identification_reliability\t[MS, MS:1002955, hr-ms compound identification confidence level, ]"
    )
    mtd_lines.append("MTD\tid_confidence_measure[1]\t[MS, MS:1002888, small molecule confidence measure, ]")
    mtd_lines.append("")
    mtd_lines.append("MTD\tsoftware[1]\t[MS, MS:1003430, OpenMS, unknown]")
    mtd_lines.append(f"MTD\tsoftware[2]\t[MS, MS:1002878, MASSter, {get_version()}]")
    mtd_lines.append("MTD\tquantification_method\t[MS, MS:1001834, LC-MS label-free quantitation analysis, ]")
    mtd_lines.append("")
    mtd_lines.append('MTD\tdatabase[1]\t[, , "no database", null]')
    mtd_lines.append("MTD\tdatabase[1]-prefix\tnull")
    mtd_lines.append("MTD\tdatabase[1]-version\tUnknown")
    mtd_lines.append("MTD\tdatabase[1]-uri\tnull")
    # mtd_lines.append('')
    for i, row in enumerate(self.samples_df.iter_rows(named=True), 1):
        mtd_lines.append(f"\nMTD\tsample[{i}]\t{row.get('sample_uid', f'sample_{i}')}")
        mtd_lines.append(f"MTD\tsample[{i}]-description\t{row.get('sample_name', 'unknown')}")
        mtd_lines.append(f"MTD\tms_run[{i}]-location\tfile://{row.get('sample_path', 'unknown')}")
        mtd_lines.append(f"MTD\tassay[{i}]\tAssay_{i}")
        mtd_lines.append(f"MTD\tassay[{i}]-sample_ref\tsample[{i}]")
        mtd_lines.append(f"MTD\tassay[{i}]-ms_run_ref\tms_run[{i}]")
    mtd_lines.append("")
    mtd_lines.append("MTD\tstudy_variable[1]\tundefined")
    mtd_lines.append("MTD\tstudy_variable[1]_refs\tundefined")
    # assay_refs = '|'.join([f"assay[{i}]" for i in range(1, len(self.samples_df)+1)])
    # mtd_lines.append(f"MTD\tstudy_variable[1]-assay_refs\t{assay_refs}")
    # mtd_lines.append("MTD\tstudy_variable[1]-description\tAll assays grouped (default)")
    with open(filename, "w", encoding="utf-8") as f:
        for line in mtd_lines:
            f.write(line + "\n")

    # --- SML (Small Molecule) table ---
    sml_lines = []
    sml_header = [
        "SMH",
        "SML_ID",
        "SMF_ID_REFS",
        "database_identifier",
        "chemical_formula",
        "smiles",
        "inchi",
        "chemical_name",
        "uri",
        "theoretical_neutral_mass",
        "adduct_ions",
        "reliability",
        "best_id_confidence_measure",
        "best_id_confidence_value",
        "opt_global_mgf_index",
    ]

    abundance_matrix = self.get_consensus_matrix()
    # Use the matrix as-is since it already has the correct sample columns
    # The matrix columns are sample names, which is what we want for the assay columns

    # round to int
    abundance_matrix = abundance_matrix.round(0)

    # Use actual number of samples from the abundance matrix
    n_assays = len(abundance_matrix.columns)
    sml_header += [f"abundance_assay[{i}]" for i in range(1, n_assays + 1)]
    sml_header += ["abundance_study_variable[1]", "abundance_variation_study_variable[1]"]
    sml_lines.append("\t".join(sml_header))

    # get adducts from consensus_df['adducts']. If value is None or [], use 'null'. If there is, take the first element and the first string
    adduct_list = []
    mapping = {
        "H1": "[M+H]+",
        "H2": "[M+2H]2+",
        "Na1": "[M+Na]+",
        "Na2": "[M+2Na]2+",
        "NH4": "[M+NH4]+",
        "HCOO": "[M+HCOO]-",
        "CH3COO": "[M+CH3COO]-",
        "H2O": "[M+H2O]+",
        "HCO2": "[M+HCO2]-",
        "H3PO4": "[M+H3PO4]+",
        "H3O1": "[M+H3O]+",
        "K1": "[M+K]+",
        "H4N1": "[M+NH4]+",
        "H-1": "[M-H]-",
        "Cl1": "[M+Cl]-",
        "Br1": "[M+Br]-",
        "I1": "[M+I]-",
        "H2O2": "[M+H2O2]+",
        "H3O2": "[M+H3O2]+",
    }
    for idx, row in enumerate(self.consensus_df.iter_rows(named=True), 1):
        adduct = "null"
        if "adducts" in row:
            row_adducts = row["adducts"]
            if isinstance(row_adducts, list) and row_adducts:
                # Each adduct is a dictionary with 'adduct' key
                first_adduct_dict = row_adducts[0]
                if isinstance(first_adduct_dict, dict) and "adduct" in first_adduct_dict:
                    adduct_str = first_adduct_dict["adduct"]
                    if adduct_str in mapping:
                        adduct = mapping[adduct_str]
                    else:
                        adduct = adduct_str

        adduct_list.append(adduct)

    for idx, row in enumerate(self.consensus_df.iter_rows(named=True), 1):
        # Get MGF indexes for this consensus feature
        mgf_indexes = mgf_mapping.get(row["consensus_uid"], [])

        sml_row = [
            "SML",
            str(idx),
            str(idx),
            str(row.get("database_identifier", "null")),
            str(row.get("chemical_formula", "null")),
            str(row.get("smiles", "null")),
            str(row.get("inchi", "null")),
            str(row.get("chemical_name", "null")),
            str(row.get("uri", "null")),
            str(row.get("theoretical_neutral_mass", "null")),
            adduct_list[idx - 1],
            str(row.get("reliability", "null")),
            str(row.get("best_id_confidence_measure", "null")),
            str(row.get("best_id_confidence_value", "null")),
            ",".join(map(str, mgf_indexes)) if mgf_indexes else "null",
        ]
        # Add abundance values for each assay
        consensus_uid = row["consensus_uid"]
        if consensus_uid in abundance_matrix.index:
            abundance_values = abundance_matrix.loc[consensus_uid].tolist()
            sml_row += [str(val) if pd.notna(val) else "null" for val in abundance_values]
        else:
            sml_row += ["null"] * n_assays
        sml_row += ["null", "null"]
        sml_lines.append("\t".join(sml_row))
    with open(filename, "a", encoding="utf-8") as f:
        f.write("\n")
        for line in sml_lines:
            f.write(line + "\n")

    # --- SMF (Small Molecule Feature) table ---
    smf_lines = []
    smf_header = [
        "SFH",
        "SMF_ID",
        "SOME_ID_REFS",
        "SOME_ID_REF_ambiguity_code",
        "adduct_ion",
        "isotopomer",
        "exp_mass_to_charge",
        "charge",
        "retention_time_in_seconds",
        "retention_time_in_seconds_start",
        "retention_time_in_seconds_end",
    ]
    smf_header += [f"abundance_assay[{i}]" for i in range(1, n_assays + 1)]
    smf_lines.append("\t".join(smf_header))

    # SMF table uses the same consensus features as SML, just different metadata
    for idx, row in enumerate(self.consensus_df.iter_rows(named=True), 1):
        smf_row = [
            "SMF",
            str(idx),
            "null",
            "null",
            adduct_list[idx - 1],  # adduct_ion
            str(row.get("isotopomer", "null")),
            str(row.get("mz", "null")),  # exp_mass_to_charge
            str(row.get("charge", "null")),
            str(row.get("rt", "null")),  # retention_time_in_seconds
            str(row.get("retention_time_in_seconds_start", "null")),
            str(row.get("retention_time_in_seconds_end", "null")),
        ]
        # Add abundance values for each assay - same as SML
        consensus_uid = row["consensus_uid"]
        if consensus_uid in abundance_matrix.index:
            abundance_values = abundance_matrix.loc[consensus_uid].tolist()
            smf_row += [str(val) if pd.notna(val) else "null" for val in abundance_values]
        else:
            smf_row += ["null"] * n_assays
        smf_lines.append("\t".join(smf_row))
    with open(filename, "a", encoding="utf-8") as f:
        f.write("\n")
        for line in smf_lines:
            f.write(line + "\n")

    # --- MGF table ---
    if include_mgf and mgf_data is not None and len(mgf_data) > 0:
        mgf_lines = []
        # Header
        mgf_header = [
            "COM",
            "MGH",
            "mgf_id",
            "prec_id",
            "prec_rt",
            "prec_mz",
            "prec_int",
            "energy",
            "level",
            "title",
            "spec_tic",
            "spec_len",
            "spec_mz",
            "spec_int",
        ]
        mgf_lines.append("\t".join(mgf_header))

        # Data rows
        for row in mgf_data.iter_rows(named=True):
            # Calculate spectrum TIC (total ion current) from the spectrum data
            spectrum_mz = row["spec_mz"]
            spectrum_inty = row["spec_int"]
            spec_tic = sum(spectrum_inty) if spectrum_inty else 0
            spec_len = row["spec_len"] if row["spec_len"] is not None else 0

            # Format spectrum data as pipe-separated strings
            spec_mz_str = "|".join([f"{mz:.4f}" for mz in spectrum_mz]) if spectrum_mz else ""
            spec_int_str = "|".join([f"{int(inty)}" for inty in spectrum_inty]) if spectrum_inty else ""

            mgf_row = [
                "COM",
                "MGF",
                str(row["mgf_index"]) if row["mgf_index"] is not None else "null",
                str(row["feature_id"]) if row["feature_id"] is not None else "null",
                f"{row['rtinseconds']:.2f}" if row["rtinseconds"] is not None else "null",
                f"{row['pepmass']:.4f}" if row["pepmass"] is not None else "null",
                "null",  # prec_int - not available in current data
                str(row["energy"]) if row["energy"] is not None else "null",
                str(row["mslevel"]) if row["mslevel"] is not None else "null",
                str(row["title"]) if row["title"] is not None else "null",
                f"{int(spec_tic)}" if spec_tic > 0 else "null",
                str(spec_len) if spec_len > 0 else "null",
                spec_mz_str if spec_mz_str else "null",
                spec_int_str if spec_int_str else "null",
            ]
            mgf_lines.append("\t".join(mgf_row))

        # Write MGF table
        with open(filename, "a", encoding="utf-8") as f:
            f.write("\n")
            for line in mgf_lines:
                f.write(line + "\n")

    if include_mgf:
        self.logger.info(f"Exported mzTab-M to {filename}")
