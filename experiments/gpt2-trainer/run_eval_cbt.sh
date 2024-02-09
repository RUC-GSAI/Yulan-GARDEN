#!/bin/bash

#SBATCH --gpus=1
#SBATCH --nodes=1
#SBATCH --job-name="evaluate cbt"
#SBATCH --output=evaluate_cbt.log

### module load anaconda/2020.11
### module load cuda/11.7
### conda activate gpt2

i=0
model_ckpt_base="models/gpt2-pt-cc-refined/step_"
while [ $i -le 2000000 ]
do
    echo $i
    cp models/gpt2-pt-cc-refined/config.json "${model_ckpt_base}${i}"
    cp models/gpt2-pt-cc-refined/tokenizer.json "${model_ckpt_base}${i}"
    ### --model_ckpt "${model_ckpt_base}${i}" \
    ### --model_ckpt /home/sunyiding/weights/gpt2 \
    accelerate launch scripts/cbt_evaluation/cbt.py \
    --model_ckpt "${model_ckpt_base}${i}" \
    --dataset_name /home/sunyiding/data/cbt/CN \
    --dataset_split test \
    --content_column sentences \
    --batch_size 1 \
    --max_eval_steps -1 \
    --seq_length 1024

    accelerate launch scripts/evaluation/cbt.py \
    --model_ckpt "${model_ckpt_base}${i}" \
    --dataset_name /home/sunyiding/data/cbt/NE \
    --dataset_split test \
    --content_column sentences \
    --batch_size 1 \
    --max_eval_steps -1 \
    --seq_length 1024
    
    i=$(expr $i + 50000)
done