# pygator/spec/__init__.py
# pygator/spec/__init__.py
"""
Spectrum analysis functions for pygator.

Available functions:
- fft_psd: Computes PSD from FFT
- welch_psd: Computes PSD using Welch method
"""

from .fft_analysis import fft_psd
from .welch_analysis import welch_psd
