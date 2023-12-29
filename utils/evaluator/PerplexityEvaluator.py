from utils.evaluator.evaluator_base import EvaluatorBase
from utils.utils import KenlmModel

from collections import defaultdict

import os

class PerplexityEvaluator(EvaluatorBase):
    '''
    The Base Class of Each Evaluator Operator, to regularize the functions of each subclass.

    Attributes:
        - no attribute for base class 'CleanerBase()'
    
    Functions:
        - evaluate_single_text(text: str): 
            ** Usage
            Evaluate a text according to the text quality of each subclass of evaluator
            
            ** Params
            @text(str): the text to be evaluated;
           
            ** Return Values
            @{{Quality Score}}: the score given by each subclass according to given text;
    '''
    def __init__(self, model_path: str = "/fs/archive/share/u2022101014/models/kenlm/", lang: str="en") -> None:
        self.input_path = ""
        self.output_path = ""
        self.langs = ["en", "zh"]
        self.models = defaultdict(str)

        if model_path:
            # load models from pretrained Kenlm
            for lang in self.langs:
                self.models[lang] = self.model = KenlmModel.from_pretrained(
                    model_path = "",
                    language=lang
                )
        else:
            self.models = None

    def evaluate_single_text(self, text: str, lang: str = "en") -> float:
        return self.models[lang].get_perplexity(text)