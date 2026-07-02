#!/bin/bash
export RANK=$SLURM_PROCID                                 # rank: process id in a task
export WORLD_RANK=$SLURM_PROCID                           # world_rank: process id
export LOCAL_RANK=$SLURM_LOCALID                          # local_rank: process relative id in a node
export WORLD_SIZE=$SLURM_NTASKS                           # world_size: number of processes
export MASTER_PORT=29500                                  # default from torch launcher
export WANDB_START_METHOD="thread"                        # WandB start method
export MASTER_ADDR=$(hostname)                            # 'localhost'
export NCCL_P2P_LEVEL=NVL                                 # use P2P by NVLink
image=nersc/pytorch:ngc-23.07-v0                          # pytorch ngc 23.07 v0
env=~/.local/perlmutter/nersc_pytorch_ngc-23.07-v0        # pytorch ngc 23.07 v0
config_file=./config/swin.yaml                            # config file
#config="swin_71var_geo_dp2_chwt_invar"                    # config name
#run_num="valid_2017_train_2021-2023_ep_100"               # export file name
config="swin_71var_geo_dp2_chwt_invar_4step"             # config name
run_num="valid_2017_train_2021-2023_ep_100"               # export file name
# nproc_per_node should be matched with batch size
torchrun --nproc_per_node=7 --nnodes=1 --node_rank=0 train.py --enable_amp --yaml_config=$config_file --config=$config --run_num=$run_num
# srun:
# -n/--ntasks                    number of tasks
# -c/--cpus-per-task             number of CPUs in each task
# --gpus-per-node                number of GPUs in each node

# bash:
# -c                             read from string

# torchrun:
# --nproc_per_node               number of processes in each node
# --nnodes                       number of nodes
# --node_rank                    rank of node
# --master_addr                  master node IP
# –master_port                   master node port
