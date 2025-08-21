# pygator/spec/fft_analysis.py
import numpy as np
import matplotlib.pyplot as plt

def fft_psd(voltage, sampling_rate, plot=True, resistance=50):
    """Compute PSD using FFT
    By default it converts voltage to power by dividing
    by a 50 Ohm resistance. Change resistance to 1 to keep it in voltage
    returns
    freq_positive: frequencies
    psd_positive: the PSD from the FFT calculation
    psd_db_per_hz: power PSD converted to dB/Hz """
    N = len(voltage)
    fft_result = np.fft.fft(voltage)
    freq = np.fft.fftfreq(N, 1/sampling_rate)
    power_spectrum = np.abs(fft_result)**2
    psd = power_spectrum / (sampling_rate * N)

    positive_freq_indices = freq > 0
    psd_positive = psd[positive_freq_indices]
    freq_positive = freq[positive_freq_indices]
    psd_positive[1:] *= 2  # double positive frequencies

    psd_db_per_hz = 10 * np.log10(psd_positive/resistance)

    if plot:
        plt.figure()
        plt.semilogx(freq_positive, psd_db_per_hz)
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Power Spectral Density (dB/Hz)')
        plt.grid(True)
        plt.show()
    
    return freq_positive, psd_positive, psd_db_per_hz
