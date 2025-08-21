# pygator/spec/welch_analysis.py
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch

def welch_psd(voltage, sampling_rate, plot=True, window='hann', average=None):
    """Compute PSD using Welch's method"""
    frequencies, psd = welch(voltage, fs=sampling_rate, nperseg=len(voltage),
                             window=window, average=average)
    # asd = np.sqrt(psd)  # amplitude spectral density

    if plot:
        plt.figure()
        plt.loglog(frequencies, np.sqrt(psd))
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('ASD (unit/sqrt(Hz))')
        plt.grid(True)
        plt.show()
    
    return frequencies, psd
