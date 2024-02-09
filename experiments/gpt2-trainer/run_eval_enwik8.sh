#!/bin/bash

#SBATCH --gpus=1
#SBATCH --nodes=1
#SBATCH --job-name="evaluate ptb"
#SBATCH --output=evaluate_ptb.log

### module load anaconda/2020.11
### module load cuda/11.7
### conda activate gpt2

i=0
model_ckpt_base="models/gpt2-pt/step_"
while [ $i -le 2000000 ]
do
    echo $i
    cp models/gpt2-pt/config.json "${model_ckpt_base}${i}"
    cp models/gpt2-pt/tokenizer.json "${model_ckpt_base}${i}"
    ### --model_ckpt /home/sunyiding/weights/gpt2 \
    ### --model_ckpt "${model_ckpt_base}${i}" \
    accelerate launch scripts/evaluate.py \
    --model_ckpt /home/sunyiding/gpt2-trainer/models/gpt2-pt \
    --dataset_name enwik8 \
    --dataset_split train \
    --content_column text \
    --batch_size 4 \
    --max_eval_steps -1 \
    --seq_length 1024
    
    i=$(expr $i + 50000)
done