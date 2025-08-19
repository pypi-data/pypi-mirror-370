import os
import pandas as pd

def xorshift(seed: int, n: int) -> list:
    numbers = []
    x = seed
    for _ in range(n):
        x ^= (x << 13) & 0xFFFFFFFF
        x ^= (x >> 17) & 0xFFFFFFFF
        x ^= (x << 5) & 0xFFFFFFFF
        numbers.append(x)
    return numbers

def generateInt(max_val: int, seed: int, index: int) -> int:
    numbers = xorshift(seed, 500)
    x = numbers[index]
    return x % (max_val + 1)

def createDf(arr, max_val: int, trial_n: int, filename: str, seed: int):
    for i in range(trial_n):
        n = generateInt(max_val, seed, i)
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
    print('Starting XORShift generation...')

    n_datasets = 20
    max_val = 10
    trial_n = 500

    data_folder = "Data"
    os.makedirs(data_folder, exist_ok=True)

    run_trial = get_next_batch_number(data_folder, n_datasets, 'XOR')

    for i in range(n_datasets):
        print(f'Generating dataset {i+run_trial}...')
        arr = []
        filename = os.path.join(data_folder, f'randoms-{i+run_trial}.csv')
        createDf(arr, max_val, trial_n, filename, seed=i+1)
    
    print('\nDone with XORShift!')

if __name__ == '__main__':
    main()