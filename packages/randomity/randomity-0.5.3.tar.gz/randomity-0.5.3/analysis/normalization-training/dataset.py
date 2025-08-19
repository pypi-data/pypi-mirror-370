import numpy as np
import os
import csv
from typing import List
import sys

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', ))
sys.path.insert(0, src_dir)

from src.randomity.generate import (
    qrandom, 
    lcg, 
    middle_square, 
    mersenne_twister, 
    xor_shift, 
    blum_blum_shub
)


def saveSeq(sequence: List[int], filename: str, data_dir: str) -> None:
    """Saves a sequence to a CSV file."""
    filepath = os.path.join(data_dir, filename)
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['n'])
        for val in sequence:
            writer.writerow([val])

def genDataset(num_sequences:int, sequence_size:int, data_dir:str):
    print("Generating sequences for the test set...")
    
    print("Numpy is generating...")
    for i in range(num_sequences):
        seq = np.random.randint(0, 1000, size=sequence_size).tolist()
        filename = f"numpy_random_{i}.csv"
        saveSeq(seq, filename, data_dir)
        
    print("LCG is generating...")
    for i in range(num_sequences):
        seq = lcg(max_val=1000, num_out=sequence_size, seed=1234+i)
        seq_norm = [val % 1000 for val in seq]
        filename = f"lcg_good_{i}.csv"
        saveSeq(seq_norm, filename, data_dir)

    print("LCG (with bad params) is generating...")
    for i in range(num_sequences):
        seq = lcg(max_val=1000, num_out=sequence_size, seed=1234+i, a=3, c=4, m=10)
        seq_norm = [val % 1000 for val in seq]
        filename = f"lcg_bad_{i}.csv"
        saveSeq(seq_norm, filename, data_dir)

    print("Middle-Square is generating...")
    for i in range(num_sequences):
        seq = middle_square(max_val=1000, num_out=sequence_size, seed=1234 + i)
        seq_norm = [val % 1000 for val in seq]
        filename = f"midsquare_{i}.csv"
        saveSeq(seq_norm, filename, data_dir)

    print("Predictable is generating...")
    for i in range(num_sequences):
        seq = [j % 1000 for j in range(sequence_size)]
        filename = f"predictable_{i}.csv"
        saveSeq(seq, filename, data_dir)

    # print("QRNG is generating...")
    # gates = ["h", "rx", "ry", "sx"]
    # for i in range(num_sequences):
    #     seq = qrandom(max_val=1000, num_out=sequence_size, q_gate=gates[i % len(gates)])
    #     filename = f"qrandom_{i}.csv"
    #     saveSeq(seq, filename, data_dir)
    #     if (i + 1) % 10 == 0:
    #             print(f"{i + 1}/{num_sequences} generated.")

    print("Mersenne Twister is generating...")
    for i in range(num_sequences):
        seq = mersenne_twister(max_val=1000, num_out=sequence_size, seed=1234+i)
        filename = f"mt_{i}.csv"
        saveSeq(seq, filename, data_dir)

    print("XOR Shift is generating...")
    for i in range(num_sequences):
        seq = xor_shift(max_val=1000, num_out=sequence_size, seed=1234+i)
        filename = f"xorshift_{i}.csv"
        saveSeq(seq, filename, data_dir)

    print("Blum Blum Shub is generating...")
    for i in range(num_sequences):
        seq = blum_blum_shub(max_val=1000, num_out=sequence_size)
        filename = f"bbs_{i}.csv"
        saveSeq(seq, filename, data_dir)

    print("Incremental is generating...")
    for i in range(num_sequences):
        seq = [j * i if i != 0 else j for j in range(sequence_size + 1)]
        filename = f"incremental_{i}.csv"
        saveSeq(seq, filename, data_dir)

    print(f"Test set saved to '{data_dir}'.")

if __name__ == '__main__':
    SEQUENCE_SIZE = 1000
    NUM_SEQUENCES = 100

    DATA_DIR = "data"
    os.makedirs(DATA_DIR, exist_ok=True)

    genDataset(num_sequences=NUM_SEQUENCES, 
               sequence_size=SEQUENCE_SIZE,
               data_dir=DATA_DIR)