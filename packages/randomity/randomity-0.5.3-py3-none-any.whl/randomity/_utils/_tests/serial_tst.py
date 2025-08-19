import numpy as np

def serial_test(data):
    """
    Performs a serial correlation test.
    """
    min_val, max_val = np.min(data), np.max(data)
    
    data_scaled = (data - min_val) / (max_val - min_val)
    if np.var(data) == 0:
        return {'serial_autocorrelation': np.nan}
        
    serial_autocorrelation = np.corrcoef(data_scaled[:-1], data_scaled[1:])[0, 1]
    
    return {'serial_autocorrelation': serial_autocorrelation}