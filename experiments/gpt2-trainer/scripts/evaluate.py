import logging
import torch
import math

from tqdm import tqdm
from accelerate import Accelerator
from arguments import EvaluationArguments
from datasets import load_dataset
from torch.utils.data import IterableDataset
from torch.utils.data.dataloader import DataLoader

from transformers import AutoModelForCausalLM, AutoTokenizer, HfArgumentParser, set_seed


class ConstantLengthDataset(IterableDataset):
    def __init__(self, tokenizer, dataset, content_column="text", seq_length=1024, num_of_sequences=1024, chars_per_token=3.6):
        self.tokenizer = tokenizer
        self.concat_token_id = tokenizer.bos_token_id
        self.dataset = dataset
        self.content_column = content_column
        self.seq_length = seq_length
        self.input_characters = seq_length * chars_per_token * num_of_sequences

    def __iter__(self):
        iterator = iter(self.dataset)
        more_examples = True
        while more_examples:
            buffer, buffer_len = [], 0
            while True:
                if buffer_len >= self.input_characters:
                    break
                try:
                    buffer.append(next(iterator)[self.content_column])
                    buffer_len += len(buffer[-1])
                except StopIteration:
                    more_examples = False
                    break
            tokenized_inputs = tokenizer(buffer, truncation=False)["input_ids"]
            all_token_ids = []
            for tokenized_input in tokenized_inputs:
                all_token_ids.extend(tokenized_input + [self.concat_token_id])
            for i in range(0, len(all_token_ids), self.seq_length):
                input_ids = all_token_ids[i : i + self.seq_length]
                if len(input_ids) == self.seq_length:
                    yield torch.tensor(input_ids)


def create_dataloader(args):
    ds_kwargs = {"streaming": True}
    eval_data = load_dataset(args.dataset_name, split=args.dataset_split, **ds_kwargs)
    eval_dataset = ConstantLengthDataset(tokenizer, eval_data, content_column=args.content_column, seq_length=args.seq_length)
    eval_dataloader = DataLoader(eval_dataset, batch_size=args.batch_size)
    return eval_dataloader


def evaluate(args):
    model.eval()
    losses = []
    for step, batch in tqdm(enumerate(eval_dataloader)):
        with torch.no_grad():
            outputs = model(batch, labels=batch)
        loss = outputs.loss.repeat(args.batch_size)
        losses.append(accelerator.gather(loss))

        if args.max_eval_steps > 0 and step >= args.max_eval_steps:
            break
    loss = torch.mean(torch.cat(losses))
    try:
        perplexity = torch.exp(loss)
    except OverflowError:
        perplexity = float("inf")
    return loss.item(), perplexity.item()


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

# Load dataset and dataloader
eval_dataloader = create_dataloader(args)

# Prepare everything with our `accelerator`.
model, eval_dataloader = accelerator.prepare(model, eval_dataloader)

# Evaluate and save the last checkpoint
logger.info("Begin to evaluate..")
eval_loss, perplexity = evaluate(args)
logger.info(f"model: {args.model_ckpt}, dataset: {args.dataset_name}")

if args.dataset_name == 'enwik8':
    logger.info(f"loss/eval: {eval_loss}, bpb: {eval_loss / math.log(2)}")
else:
    logger.info(f"loss/eval: {eval_loss}, perplexity: {perplexity}")
