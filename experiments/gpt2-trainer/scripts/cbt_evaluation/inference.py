import torch
import json

from tqdm import tqdm
from datasets import load_dataset, Dataset
from torch.utils.data import IterableDataset
from transformers import AutoModelForCausalLM, AutoTokenizer
from torch.utils.data.dataloader import DataLoader

DATA_INPUT_DIR = "/home/sunyiding/data/coqa/coqa-dev-v1.0.json"
OUTPUT_PATH = "./dev-inference.json"

# Load pre-trained model and tokenizer
model_path = '/home/sunyiding/weights/gpt2'
model = AutoModelForCausalLM.from_pretrained(model_path, max_length=1024)
tokenizer = AutoTokenizer.from_pretrained(model_path)

class CoQADataset(IterableDataset):
    def __init__(self, tokenizer, dataset):
        self.tokenizer = tokenizer
        self.dataset = dataset
        self.story_column = "story"
        self.question_column = "questions"
        self.answer_column = "answers"

    def __iter__(self):
        iterator = iter(self.dataset)
        while True:
            try:
                cur = next(iterator) 
                ret = {
                    "id": cur["id"],
                    "story": cur["story"],
                    "questions": cur["questions"]
                }
                yield ret
            except StopIteration:
                break

ds_kwargs = {"streaming": True}

with open(DATA_INPUT_DIR, mode='r', encoding='utf-8') as fr:
    dt = json.loads(fr.read())
print(len(dt["data"]))
eval_data = Dataset.from_list(dt["data"])
# eval_data = load_dataset("/home/sunyiding/data/coqa/coqa-dev-v1.0.json", **ds_kwargs)
eval_dataset = CoQADataset(tokenizer, eval_data)
eval_dataloader = DataLoader(eval_dataset, batch_size=1)


def evaluate(model, eval_dataloader, output_path, device):
    # Set model to evaluation mode
    model.eval()
    ret = []
    for step, batch in tqdm(enumerate(eval_dataloader)):
        story_id = batch["id"][0]
        story = batch["story"][0]
        questions = batch["questions"]
        # print(batch)
        # assert 0
        prompt_tokens = tokenizer.encode(story, return_tensors='pt').to(device)
        # Generate Response
        response = ''
        for _ in range(len(questions)):
            cur_question = questions[_]
            cur_input_text = cur_question["input_text"][0]
            cur_turn_id = _ + 1
            with torch.no_grad():
                cur_input_tokens = tokenizer.encode(cur_input_text, return_tensors='pt').to(device)
                prompt_tokens = torch.cat([prompt_tokens, cur_input_tokens], dim=1)
                if prompt_tokens.size(-1) < 1024:
                    # Generate output from the model
                    output = model.generate(prompt_tokens, max_tokens=1000, pad_token_id=tokenizer.eos_token_id, 
                                        num_return_sequences=1, do_sample=True)

                    # Decode the output tokens
                    response = tokenizer.decode(output[0], skip_special_tokens=True)
                    cur_response = response.removeprefix(tokenizer.decode(prompt_tokens[0], skip_special_tokens=True))
                    # print(f"Round {turn_id}: {cur_response}")

                    # Extend the prompt with the response
                    prompt_tokens = torch.cat([output], dim=1)
                else:
                    cur_response = ""
                ret.append({
                    "id": story_id,
                    "turn_id": cur_turn_id,
                    "answer": cur_response
                })
    
    with open(output_path, mode='w', encoding='utf-8') as fw:
        fw.write(str(ret))


if __name__ == '__main__':
    # Set device to GPU if available
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    evaluate(model, eval_dataloader=eval_dataloader, output_path=OUTPUT_PATH, device=device)
    # # Example usage
    # prompt = "Once upon a time, in a barn near a farm house, there lived a little white kitten named Cotton. Cotton lived high up in a nice warm place above the barn where all of the farmer's horses slept. But Cotton wasn't alone in her little home above the barn, oh no. She shared her hay bed with her mommy and 5 other sisters. All of her sisters were cute and fluffy, like Cotton. But she was the only white one in the bunch. The rest of her sisters were all orange with beautiful white tiger stripes like Cotton's mommy. Being different made Cotton quite sad. She often wished she looked like the rest of her family. So one day, when Cotton found a can of the old farmer's orange paint, she used it to paint herself like them. When her mommy and sisters found her they started laughing. \n\n\"What are you doing, Cotton?!\" \n\n\"I only wanted to be more like you\". \n\nCotton's mommy rubbed her face on Cotton's and said \"Oh Cotton, but your fur is so pretty and special, like you. We would never want you to be any other way\". And with that, Cotton's mommy picked her up and dropped her into a big bucket of water. When Cotton came out she was herself again. Her sisters licked her face until Cotton's fur was all all dry. \n\n\"Don't ever do that again, Cotton!\" they all cried. \"Next time you might mess up that pretty white fur of yours and we wouldn't want that!\" \n\nThen Cotton thought, \"I change my mind. I like being special\". What color was Cotton? "
    # response = generate_response(prompt, model, tokenizer, device=device, num_turns=3)
    # # print(response)