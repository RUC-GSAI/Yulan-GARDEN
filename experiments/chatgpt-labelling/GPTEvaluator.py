import time
import json
import os
import openai
from openai import OpenAI
from tqdm import tqdm
from collections import defaultdict

from evaluator_base import *

raw_dt = []
refined_dt = []
mixed_dt = []

class GPTEvaluator(EvaluatorBase):
    def __init__(self, api_keys: list = ["/your/OpenAI/API/here"]):
        self.api_keys = api_keys
        self.OpenAIs = []
        for api_key in self.api_keys:
            self.OpenAIs.append(OpenAI(api_key=api_key))
        self.cur_OpenAIs_ptr = 0
        self.MAX_RETRY_LIMITS_PER_QUERY = max(3, len(self.OpenAIs))
        self.MAX_LENGTH_PROMPT = 24576
        self.input_path = ""
        self.output_path = ""
    
    def _try_next_OpenAI(self):
        self.cur_OpenAIs_ptr = (self.cur_OpenAIs_ptr + 1) % len(self.OpenAIs)
        if len(self.OpenAIs) == 1:
            print("No available OpenAI accounts AnyMore, please try later")

    def _get_cur_OpenAI(self):
        return self.OpenAIs[self.cur_OpenAIs_ptr]

    def evaluate_single_pair(self, text1: str, text2: str, lang: str = "Chinese", model: str = "gpt-3.5-turbo-1106") -> int:
        '''
        To compare {{text1}} with {{text2}} according to the text quality, toxicity by gpt-4(gpt-3.5-turbo).

        Given "Text 1" or "Text 2" or "Tied" to indicate the result answered by model.

        Params:
            @text1: text to be evaluated, 
            @text2: text to be evaluated,
            @lang: text language should be predefined (zh: Chinese, en: English),
            @model: gpt model to evaluate
        '''
        prompt = f"""Evaluate which of the two given {lang} texts([Text 1] and [Text 2]) is more suitable for training a language model. The texts are collected from websites. The texts contain some unuse signals which is harmful to the language model. After we refined the texts, they should be neatly formatted, locally fluent and logical, although it doesn't have to be fully self-contained and can consist of multiple subparts. It is important to ensure the absence of any toxic content. Besides, personally sensitive information is acceptable. This is my basic requirement but you have certain freedom to judge its suitability based on your own knowledge. 

Please only answer "Text 1" or "Text 2" or "Tied" without offering any explanation. "Tied" means the two text given comparable quality.

[Text 1]
{text1}

[Text 2]
{text2}
"""
        if len(prompt) >= self.MAX_LENGTH_PROMPT:
            return "TOO LONG TO EVALUATE"

        retry_cnt = 0
        while True:
            try:
                result = self._get_cur_OpenAI().chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are ChatGPT, a large language model trained by OpenAI, based on the GPT-3.5 architecture."},
                        {"role": "user", "content": "{}".format(prompt)},
                    ],
                    n = 1,
                )
                answer = result.choices[0].message.content
            except openai.RateLimitError:
                self._try_next_OpenAI()
                retry_cnt += 1
                if retry_cnt >= self.MAX_RETRY_LIMITS_PER_QUERY:
                    raise Exception(f"Tried {retry_cnt} times exceed the limit {self.MAX_RETRY_LIMITS_PER_QUERY} in function GPTEvaluator().evaluate_single_pair()")
            except openai.BadRequestError:
                answer = "UNKNOWN ERROR"                
                break
            else:
                break

        return answer

    def evaluate_pairwise_pairs(self, text_pair_lis: list, input_path: str = "", output_path: str = "") -> None:
        '''
        To evaluate each text pair in {{text_pair_lis}}, each element in {{text_pair_lis}} should be a list contained two string.

        Params:
            @text_pair_lis: a list contained texts to be evaluated, format like: [{"text1": "这是一段文本", "text2": "適湜①葮焱暒妏", "lang": "Chinese"}, {"text1": "Hello World!", "text2": "Motherf***er!", "lang": "English"}, ...];
            @output_path: the output path to save evaluation report. If no path is given, the report will be outputed into self.output_path;
        '''
        if input_path:
            text_pair_lis = []
            with open(input_path, mode='r', encoding='utf-8') as fr:
                for line in fr:
                    text_pair_lis.append(json.loads(line))
        if output_path:
            self.output_path = output_path
        cnt_dict = defaultdict(int)
        with open(os.path.join(self.output_path, f"pairwise_report_{self._now_timestamp()}.jsonl"), mode='w', encoding='utf-8') as fw:
            for each in tqdm(text_pair_lis):
                answer = self.evaluate_single_pair(
                    text1 = each['text1'],
                    text2 = each['text2'],
                    lang = each['lang']
                )
                cnt_dict[answer] += 1
                each['evaluate_ans'] = answer 
                fw.write(json.dumps(each, ensure_ascii=False) + '\n')
        print(cnt_dict)
        

if __name__ == '__main__':
    gptevaluator = GPTEvaluator(
        api_keys=[
            "",
            ""
        ]
    )
    raw_path = "/path/to/raw/data"
    refined_path = "/path/to/refined/data"

    with open(raw_path, mode='r', encoding='utf-8') as fr:
        for line in fr:
            raw_dt.append(json.loads(line)["text"])
    
    with open(refined_path, mode='r', encoding='utf-8') as fr:
        for line in fr:
            refined_dt.append(json.loads(line)["text"])
    
    assert len(raw_dt) == len(refined_dt)

    for i in range(0, len(raw_dt)):
        if raw_dt[i] != refined_dt[i]:
            mixed_dt.append({
                "text1": raw_dt[i],
                "text2": refined_dt[i],
                "lang": "/corresponding/language/label"
            })

    gptevaluator.evaluate_pairwise_pairs(
        text_pair_lis=mixed_dt,
        input_path="",
        output_path="./"
    )