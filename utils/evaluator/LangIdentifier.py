from utils.evaluator.evaluator_base import EvaluatorBase

import time
import json
import os
import fasttext
from tqdm import tqdm
from collections import defaultdict

class LangIdentifier(EvaluatorBase):
    def __init__(self, model_path: str="utils/models/fasttext/lid.176.bin"):
        self.input_path = ""
        self.output_path = ""
        self.reject_threshold = 0.5
        if model_path:
            self.model = fasttext.load_model(model_path)
        else:
            self.model = None

    def _regularize_text(self, text: str) -> str:
        ret = text
        replace_list = ['\n']
        for replace_char in replace_list:
            ret = ret.replace(replace_char, '')
        return ret

    def evaluate_single_text(self, text: str) -> (set, float):
        text = self._regularize_text(text)
        labels, scores = self.model.predict(text)
        labels = [label.replace('__label__', '') for label in labels]
        return labels, scores


if __name__ == '__main__':
    langidentifier = LangIdentifier(
        model_path="utils/models/fasttext/lid.176.bin"
    )
    texts=[
       "I love openai too much! It invented ChatGPT and GPT4 such tramendous inventions!!",
       "这是一段文本",
       "I lov\n\ne open\ni too much! It in  ve\tnted ChatG PT and GPT4 such tra me\tndous inv\tenti\tons!!",
       "適\n\n\t\n湜①\n葮焱\t暒 妏",
       "这是一段文本",
       "I love openai too <br> much! It invented ChatGPT and GPT4 such </br> tramendous inventions!!",
    ]
    for text in texts:
        label, score = langidentifier.evaluate_single_text(text)
        print(label, score)