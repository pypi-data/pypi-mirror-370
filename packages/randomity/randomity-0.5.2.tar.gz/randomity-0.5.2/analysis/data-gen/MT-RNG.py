import os
import pandas as pd
import numpy as np

def generateInt(max_val: int, rng) -> int:
    return rng.randint(0, max_val + 1)

def createDf(arr, max_val: int, trial_n: int, filename: str, seed: int):
    rng = np.random.RandomState(seed)
    for i in range(trial_n):
        n = generateInt(max_val, rng)
        arr.append({'index': i, 'n': n})
        if i % 50 == 0:
            print(f"Trial {i+1}/{trial_n}")
    
    df = pd.DataFrame(arr)
    df.to_csv(filename, index=False)

def get_next_batch_number(data_folder: str, n_datasets: int, prefix: str) -> int:
    existing_files = [f for f in os.listdir(data_folder) if f.startswith('randoms-') and f.endswith('.csv')]
    if not existing_files:
        return 1
    
    numbers = [int(f.replace('randoms-', '').replace('.csv', '')) for f in existing_files]
    highest_num = max(numbers)
    return highest_num + 1

def main():
    print('Starting Mersenne Twister generation...')

    n_datasets = 20
    max_val = 10
    trial_n = 500

    data_folder = "Data"
    os.makedirs(data_folder, exist_ok=True)

    run_trial = get_next_batch_number(data_folder, n_datasets, 'MT')

    for i in range(n_datasets):
        print(f'Generating dataset {i+run_trial}...')
        arr = []
        filename = os.path.join(data_folder, f'randoms-{i+run_trial}.csv')
        createDf(arr, max_val, trial_n, filename, seed=i+1)
    
    print('\nDone with Mersenne Twister!')

if __name__ == '__main__':
    main()