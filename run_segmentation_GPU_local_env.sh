#!/bin/bash -l

############# SLURM SETTINGS #############
#SBATCH --account=none   # account name (mandatory), if the job runs under a project then it'll be the project name, if not then it should =none
#SBATCH --job-name=run_segmentation   # some descriptive job name of your choice
#SBATCH --output=%x-%j_out.txt      # output file name will contain job name + job ID
#SBATCH --error=%x-%j_err.txt       # error file name will contain job name + job ID
#SBATCH --gres=gpu:1
#SBATCH --partition=gpu            # which partition to use, default on MARS is “nodes"
#SBATCH --time=0-06:00:00          # time limit for the whole run, in the form of d-hh:mm:ss, also accepts mm, mm:ss, hh:mm:ss, d-hh, d-hh:mm
#SBATCH --mem-per-gpu=64G           # memory required per node, in the form of [num][M|G|T]
#SBATCH --nodes=1              # number of nodes to allocate, default is 1
#SBATCH --ntasks=4             # number of Slurm tasks to be launched, increase for multi-process runs ex. SPECIFY even for the GPU
#SBATCH --cpus-per-task=8      # number of processor cores to be assigned for each task, default is 1, increase for multi-threaded runs or GPU
#SBATCH --ntasks-per-node=4     # number of tasks to be launched on each allocated node

############# LOADING MODULES (optional) #############
module purge
source /users/ad394h/miniforge-pypy3/etc/profile.d/mamba.sh
mamba activate segmentation
echo "Hello from $SLURM_JOB_NODELIST"
echo "mamba environment is $CONDA_DEFAULT_ENV"

############# MY CODE #############

# python3 /users/ad394h/Documents/scripts/tumor_normal_digital_brain_tumor_final.py
# python3 /users/ad394h/Documents/segment_blood_vessels/src/histosegnet_base_model.py
python3 /users/ad394h/Documents/scripts/check_GPU_resources.py
echo "this means code ran well"
############# END #############
mamba deactivate

echo "mamba default environment is $CONDA_DEFAULT_ENV" 

echo "$CONDA_PREFIX" 