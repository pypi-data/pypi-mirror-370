## Data

This directory contains the data files used for a proof of concept (PoC) for the test suite and randomness scoring. The source code used to generate these samples is available in the [data-gen](/analysis/data-gen/) directory.

Each folder in this directory holds samples for a specific random number generator (RNG):

- [LCG-RN](/analysis/data/LCG-RN/): Linear Congruential Generator.
- [MT-RN](/analysis/data/MT-RN/): Mersenne Twister Generator.
- [XORShift-RN](/analysis/data/XORShift-RN/): XOR Shift Generator.
- [Q-RN](/analysis/data/Q-RN/): Quantum Random Number Generator.
- [summary](/analysis/data/vectors/): Summary vectors holding the results of the analysis, by generator, source, and full results.