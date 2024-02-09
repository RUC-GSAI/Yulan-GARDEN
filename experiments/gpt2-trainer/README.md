# GPT-2-trainer

## Quick Start

Install the dependencies simply run the following command:
```bash
pip install -r requirements.txt
```

Login the huggingface-cli.

```bash
huggingface-cli login
```

## Tokenizer
You can train a new tokenizer, or just simply using the official tokenizer of GPT-2: 
```bash
python scripts/bpe_training.py \
    --base_tokenizer gpt2 \
    --dataset_name /path/to/tokenizer/training/corpus
```

## Training

To randomly initialize a new GPT-2 model with 110M parameters you can run:

```bash
python scripts/initialize_model.py \
--config_name gpt2 \
--model_name models/gpt2-init
```

The main training script is built with `accelerate` to scale across a wide range of platforms and infrastructure scales. We train two models with 110M parameters for one week with only one RTX3090 (24GB RAM).

Configure `accelerate` and login to Weights & Biases:

```bash
accelerate config
wandb login
```

We utilize FP16 mix precision training techniques here. To train gpt2-pt-cc-raw and gpt2-pt-cc-refined with raw and refined dataset respectively, you can simply run our scripts:

```bash
nohup bash run_pt_cc_raw.sh 2>&1 >logs/pt_cc_raw.log &
nohup bash run_pt_cc_refined.sh 2>&1 >logs/pt_cc_refined.log &
```

It will save checkpoints every 0.05M steps, you can also modify to customized your own training configuration settings for [gpt2-pt-cc-raw](./run_pt_cc_raw.sh) and [gpt2-pt-cc-refined](./run_pt_cc_refined.sh).

## Evaluation

To align with GPT-2, we provide some scripts to evaluate the language modeling ability of our pretrained foundation models.

Take WikiText103 dataset as an example, You can simply run:
```bash
bash run_eval_wikitext103.sh
```