import numpy as np

def ftt_test(data):
    """
    Performs a Fast Fourier Transform test.
    """
    n = len(data)
    if n < 2:
        return {'fft_dominant_frequency': np.nan, 'fft_dominant_period': np.nan, 'fft_max_magnitude': np.nan}
        
    fft_result = np.fft.fft(data)
    magnitudes = np.abs(fft_result)
    frequencies = np.fft.fftfreq(n)
    
    half_n = n // 2
    if half_n < 2:
        return {'fft_dominant_frequency': np.nan, 'fft_dominant_period': np.nan, 'fft_max_magnitude': np.nan}
    
    dominant_index = np.argmax(magnitudes[1:half_n+1]) + 1
    dominant_magnitude = magnitudes[dominant_index]
    dominant_frequency = frequencies[dominant_index]
    dominant_period = 1 / dominant_frequency if dominant_frequency > 0 else np.nan
    
    return {
        'fft_dominant_frequency': dominant_frequency,
        'fft_dominant_period': dominant_period,
        'fft_max_magnitude': dominant_magnitude
    }