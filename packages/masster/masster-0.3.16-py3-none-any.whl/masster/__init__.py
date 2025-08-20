"""
masster - Mass Spectrometry Analysis Assistant

A comprehensive Python package for processing and analyzing untargeted metabolomics data,
supporting both DDA (Data-Dependent Acquisition) and DIA (Data-Independent Acquisition)
mass spectrometry workflows.
"""

from __future__ import annotations

from masster._version import __version__

# from masster._version import get_version
from masster.chromatogram import Chromatogram
from masster.sample.sample import Sample
from masster.spectrum import Spectrum
from masster.study.study import Study


__all__ = [
    "Chromatogram",
    "Sample",
    "Spectrum",
    "Study",
    "__version__",
    #    "get_version",
]
