#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=20
#SBATCH --time 01:00:00
#SBATCH --output=python_output_LAB2_1.txt

module load StdEnv/2-23 python/3.13.2 scipy-stack/2026a

python Lab2_1.py