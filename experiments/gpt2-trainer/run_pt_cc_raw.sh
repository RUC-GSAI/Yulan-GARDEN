#!/bin/bash

#SBATCH --gpus=1
#SBATCH --nodes=1
#SBATCH --job-name="pt_gpt2_cc_raw"
#SBATCH --output=pt_gpt2_cc_raw.log

### module load anaconda/2020.11
### module load cuda/11.7
### source activate gpt2

accelerate launch scripts/gpt2_pt.py \
--model_ckpt models/gpt2-init \
--save_dir models/gpt2-pt-cc-raw \
--dataset_name_train /path/to/raw/training/data \
--dataset_name_valid /path/to/raw/validation/data \
--train_batch_size 6 \
--valid_batch_size 6 \
--learning_rate 5e-4 \
--num_warmup_steps 5000 \
--gradient_accumulation 1 \
--gradient_checkpointing False \
--max_train_steps 2000000 \
--save_checkpoint_steps 10000
