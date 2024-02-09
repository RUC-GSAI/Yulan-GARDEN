import logging

import torch
from tqdm import tqdm
from accelerate import Accelerator
from arguments import EvaluationArguments
from datasets import load_dataset
from torch.utils.data import IterableDataset
from torch.utils.data.dataloader import DataLoader

from transformers import AutoModelForCausalLM, AutoTokenizer, HfArgumentParser, set_seed

class CBTDataset(IterableDataset):
    def __init__(self, tokenizer, dataset):
        self.tokenizer = tokenizer
        self.dataset = dataset
        self.mask = "XXXXX"
        self.sentence_column = "sentences"
        self.question_column = "question"
        self.answer_column = "answer"
        self.options_column = "options"

    def __iter__(self):
        iterator = iter(self.dataset)
        while True:
            try:
                cur = next(iterator)
                ret = []
                options = cur[self.options_column]
                for option in options:
                    text = '\n'.join(cur[self.sentence_column])
                    text = f"{text}\n{cur[self.question_column].replace(self.mask, option)}"
                    tmp = {
                        # "text": text,
                        "tokenized_text": torch.tensor(self.tokenizer(text, return_tensors="pt")["input_ids"]),
                        "answer": option == cur[self.answer_column]
                    }
                    ret.append(tmp)
                yield ret
            except StopIteration:
                break

def create_dataloader(args):
    ds_kwargs = {"streaming": True}
    eval_data = load_dataset(args.dataset_name, split=args.dataset_split, **ds_kwargs)
    eval_dataset = CBTDataset(tokenizer, eval_data)
    eval_dataloader = DataLoader(eval_dataset, batch_size=1)
    return eval_dataloader


def evaluate(args):
    model.eval()
    tot_cnt, acc_cnt, fail_cnt = 1, 1, 0
    for step, batch in tqdm(enumerate(eval_dataloader), desc=f""):
        with torch.no_grad():
            losses, true_loss = [], 0
            # try:
            print(tot_cnt, acc_cnt, acc_cnt / tot_cnt)

            example = batch[0]
            tokenized_ids = example['tokenized_text']
            context_length = tokenized_ids.size(-1)

            if context_length > 1024:
                fail_cnt += 1
                continue

            for each in batch:
                tokenized_ids = each['tokenized_text']
                answer = each['answer']
                context_length = tokenized_ids.size(-1)
                # odict_keys(['loss', 'logits', 'past_key_values'])
                outputs = model(tokenized_ids, labels=tokenized_ids)
                loss = outputs.loss
                losses.append(loss)
                if answer:
                    true_loss = loss
            mini_loss = min(losses)
            tot_cnt += 1
            if mini_loss == true_loss:
                acc_cnt += 1
            # except:
                # continue

    return acc_cnt, tot_cnt, fail_cnt


# Setup Accelerator
accelerator = Accelerator()

# Parse configuration
parser = HfArgumentParser(EvaluationArguments)
args = parser.parse_args()
set_seed(args.seed)

# Logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s", datefmt="%m/%d/%Y %H:%M:%S", level=logging.INFO
)

# Load model and tokenizer
model = AutoModelForCausalLM.from_pretrained(args.model_ckpt)
tokenizer = AutoTokenizer.from_pretrained(args.model_ckpt)
# tokenizer.pad_token = tokenizer.eos_token

# Load dataset and dataloader
eval_dataloader = create_dataloader(args)

# Prepare everything with our `accelerator`.
model, eval_dataloader = accelerator.prepare(model, eval_dataloader)

# Evaluate and save the last checkpoint
logger.info("Begin to evaluate..")
acc_cnt, tot_cnt, fail_cnt = evaluate(args)
logger.info(f"model: {args.model_ckpt}, dataset: {args.dataset_name}")
logger.info(f"acc: {acc_cnt / tot_cnt}, acc_cnt: {acc_cnt}, tot_cnt: {tot_cnt}, fail_cnt: {fail_cnt}")
