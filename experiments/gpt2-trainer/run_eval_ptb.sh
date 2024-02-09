#!/bin/bash

#SBATCH --gpus=1
#SBATCH --nodes=1
#SBATCH --job-name="evaluate ptb"
#SBATCH --output=evaluate_ptb.log

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
    ### --model_ckpt /home/sunyiding/weights/gpt2 \
    ### --model_ckpt "${model_ckpt_base}${i}" \
    ### --model_ckpt /home/sunyiding/gpt2-trainer/models/gpt2-pt \

    accelerate launch scripts/evaluate.py \
    --model_ckpt "${model_ckpt_base}${i}" \
    --dataset_name /home/sunyiding/data/ptb_text_only \
    --dataset_split test \
    --content_column sentence \
    --batch_size 4 \
    --max_eval_steps -1 \
    --seq_length 1024
    
    i=$(expr $i + 50000)
done