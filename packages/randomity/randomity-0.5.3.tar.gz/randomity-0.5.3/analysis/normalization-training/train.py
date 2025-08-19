import os
import sys
import pandas as pd

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', ))
sys.path.insert(0, project_root)

from src.randomity._utils import _gen_test_vector


def train_normalization_parameters(data_dir: str = 'data') -> dict:
    """
    Computes min/max values for non-p-value features across the entire dataset
    to be used for normalization.

    Args:
        data_dir (str): The directory where the sequence CSVs are stored (from dataset.py).

    Returns:
        dict: A dictionary containing the min and max values for each feature.
    """
    normalization_features = [
        'eqdist_diff', 
        'serial_autocorrelation', 
        'entropy_val', 
        'fft_max_magnitude'
    ]

    all_results = []
    
    if not os.path.exists(data_dir):
        print(f"Error: Data directory '{data_dir}' not found.")
        return {}

    print(f"Starting analysis on sequences in '{data_dir}'...")
    for filename in os.listdir(data_dir):
        if filename.endswith('.csv'):
            filepath = os.path.join(data_dir, filename)
            
            try:
                sequence = pd.read_csv(filepath)['n'].tolist()
                
                test_vector_dict = _gen_test_vector(sequence)
                
                all_results.append(test_vector_dict)

                if len(all_results) % 100 == 0:
                    print(f"Processed {len(all_results)}/{len(os.listdir(data_dir))}")

            except Exception as e:
                print(f"Skipping file '{filename}' due to an error: {e}")

    if not all_results:
        print("No valid sequences were processed. Cannot compute normalization parameters.")
        return {}

    all_results_df = pd.DataFrame(all_results)
    
    min_max_params = {}
    for feat in normalization_features:
        if feat in all_results_df.columns:
            min_val = all_results_df[feat].min()
            max_val = all_results_df[feat].max()
            min_max_params[feat] = {'min': min_val, 'max': max_val}
            
    return min_max_params


if __name__ == "__main__":
    normalization_params = train_normalization_parameters(data_dir='data')
    
    if normalization_params:
        print("\nNormalization Parameters:")
        print(normalization_params)
        
        config_path = 'normalization_config.py'
        with open(config_path, 'w') as f:
            f.write("NORMALIZATION_PARAMS = {\n")
            for feat, vals in normalization_params.items():
                f.write(f"    '{feat}': {{'min': {vals['min']}, 'max': {vals['max']}}},\n")
            f.write("}\n")
            
        print(f"\nSaved normalization parameters to '{config_path}'")