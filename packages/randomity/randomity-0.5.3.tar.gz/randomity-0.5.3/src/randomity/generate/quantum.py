from qiskit import QuantumCircuit
from qiskit_aer import Aer
from qiskit import transpile
from math import ceil, log2
from math import pi

import warnings
warnings.filterwarnings("ignore")

from .._utils.check_param import _checkParam_qrandom
from .._utils.draw_histogram import _draw_histogram

def qrandom(min_val:int=0, 
            max_val:int=10,
            num_out:int=1, 
            q_gate:str="h",
            hist=False) -> list[int]:
    """
    Generate a random number using quantum mechanics.

    Args:
        min_val (integer): Minimum value of the random number. Default is 0.
        max_val (integer): Maximum value of the random number. Default is 10.
        num_out (integer): Number of numbers to generate. Default is 1.
        q_gate (string): Quantum gate to put on the qubit(s). Options are:
                        - "h" (Hadamard gate),
                        - "rx" (Rotation-X gate),
                        - "ry" (Rotation-Y gate),
                        - "sx" (Square root of X gate).
                    Default is "h" (Hadamard gate).
        hist (boolean): Whether to display a histogram of the generated numbers. Default is False.

    Returns:
        A list of random integers.
    """
    _checkParam_qrandom(min_val, max_val, num_out, q_gate, hist)

    random_numbers = []

    for _ in range(num_out):
        random_int = generateInt(max_val - min_val, q_gate)
        shifted_int = random_int + min_val
        random_numbers.append(shifted_int)

    if hist:
        _draw_histogram(random_numbers, 
             bins=10, 
             title='Histogram of Random Numbers', 
             xlabel='Value', 
             ylabel='Frequency', 
             color='tab:red', 
             alpha=0.7, 
             edgecolor='black',
             grid=True)

    return random_numbers

def generateBit(gate:str="h") -> int:
    qc = QuantumCircuit(1, 1)

    # Hadamard gate
    if gate == "h":
        qc.h(0)
    # Rotation-X gate
    elif gate == "rx":
        qc.rx(pi/2, 0)
    # Rotation-Y gate
    elif gate == "ry":
        qc.ry(pi/2, 0)
    # Square root of X gate
    elif gate == "sx":
        qc.sx(0)
    else:
        qc.h(0)

    qc.measure(0, 0)

    backend = Aer.get_backend('qasm_simulator')
    transpiled_qc = transpile(qc, backend)
    job = backend.run(transpiled_qc, shots=1, memory=True)
    result = job.result()

    measured_result = int(result.get_memory()[0])

    return measured_result

def generateInt(max_val: int, q_gate: str) -> int:
    nBits = ceil(log2(max_val + 1))
    while True:
        bits = [generateBit(q_gate) for _ in range(nBits)]
        random_number = sum(bit * (2 ** i) for i, bit in enumerate(reversed(bits)))
        if random_number <= max_val:
            return random_number