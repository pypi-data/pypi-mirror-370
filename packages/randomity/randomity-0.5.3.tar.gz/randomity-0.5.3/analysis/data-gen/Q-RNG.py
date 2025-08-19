import os
from qiskit import QuantumCircuit
from qiskit_aer import Aer
from qiskit import transpile
from qiskit_ibm_runtime import QiskitRuntimeService
import pandas as pd
from math import ceil, log2

def generateBit() -> int:
    service = QiskitRuntimeService()

    qc = QuantumCircuit(1, 1)
    qc.h(0)
    qc.measure(0, 0)

    backend = service.get_backend("ibm_brisbane")
    transpiled_qc = transpile(qc, backend)
    job = backend.run(transpiled_qc)
    result = job.result()

    counts = result.get_counts()
    measured_result = int(list(counts.keys())[0])

    return measured_result

def generateInt(max_val: int):
    nBits = ceil(log2(max_val + 1))
    
    while True:
        bits = [generateBit() for _ in range(nBits)]
        random_number = sum(bit * (2 ** i) for i, bit in enumerate(reversed(bits)))

        if random_number <= max_val:
            return random_number
        
def createDf(arr, max_val: int, trial_n: int, filename: str):
    for i in range(trial_n):
        n = generateInt(max_val)
        arr.append({'index': i, 'n': n})
        if i % 50 == 0:
            print(f"Trial {i+1}/{trial_n}")

    df = pd.DataFrame(arr)
    df.to_csv(filename, index=False)

def get_next_batch_number(data_folder: str, n_datasets: int) -> int:
    existing_files = [f for f in os.listdir(data_folder) if f.startswith('randoms-') and f.endswith('.csv')]
    if not existing_files:
        return 1
    
    numbers = []
    for f in existing_files:
        num_str = f.replace('randoms-', '').replace('.csv', '')
        numbers.append(int(num_str))
    
    highest_num = max(numbers)
    return highest_num + 1

def main():
    n_datasets = 60
    max_val = 10
    trial_n = 500

    data_folder = "Data"
    os.makedirs(data_folder, exist_ok=True)

    run_trial = get_next_batch_number(data_folder, n_datasets)

    for i in range(n_datasets):
        print(f'Generating dataset {i+run_trial}...')
        arr = []
        filename = os.path.join(data_folder, f'randoms-{i+run_trial}.csv')
        createDf(arr, max_val, trial_n, filename)

if __name__ == '__main__':
    main()