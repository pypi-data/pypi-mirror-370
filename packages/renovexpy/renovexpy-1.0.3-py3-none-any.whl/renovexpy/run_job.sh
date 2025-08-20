#!/bin/bash
#Set job requirements
#SBATCH -N 1
#SBATCH --tasks-per-node=128
#SBATCH -t 1:00:00
 
#Loading modules
#module load 2023
# module load Miniconda3/23.5.2-0
source /sw/arch/RHEL8/EB_production/2023/software/Miniconda3/23.5.2-0/etc/profile.d/conda.sh
conda activate renovexpy

#Copy input file to scratch
# cp $HOME/big_input_file "$TMPDIR"
 
#Create output directory on scratch
# mkdir "$TMPDIR"/output_dir
 
#Execute a Python program located in $HOME, that takes an input file and output directory as arguments.
python off_the_fly.py
 
#Copy output directory from scratch to home
# cp -r "$TMPDIR"/output_dir $HOME
