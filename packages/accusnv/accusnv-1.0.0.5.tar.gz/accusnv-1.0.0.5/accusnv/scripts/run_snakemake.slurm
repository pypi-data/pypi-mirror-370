#!/bin/bash
#SBATCH --job-name widevariant.main
#SBATCH -n 1
#SBATCH -p newnodes,sched_mit_tami,mit_normal,mit_normal_gpu,mit_preemptable
#SBATCH --time=10:00:00
#SBATCH --mem=50GB
#SBATCH -o mainout.txt
#SBATCH -e mainerr.txt
#SBATCH --mail-user=YOUR_EMAIL_HERE
#SBATCH --mail-type=ALL
# Activate conda environment (may need to change name of env)
#source activate snakemake
snakemake  --profile giga/cdi/conf
# Print "Done!!!" at end of main log file
echo Done!!!
