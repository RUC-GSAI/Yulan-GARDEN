from utils.evaluator.evaluator_base import EvaluatorBase
from utils.utils.kenlm_model import KenlmModel

from collections import defaultdict

from typing import Union

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
    def __init__(self, model_path: str = "utils/models/kenlm/", lang: str="en") -> None:
        self.input_path = ""
        self.output_path = ""
        self.langs = ["en", "zh"]
        self.models = defaultdict(str)

        if model_path:
            # load models from pretrained Kenlm
            for lang in self.langs:
                self.models[lang] = self.model = KenlmModel.from_pretrained(
                    model_path=model_path,
                    language=lang
                )
        else:
            self.models = None

    def evaluate_single_text(self, text: str, lang: str = "en") -> Union[float, None]:
        if lang in self.langs:
            return self.models[lang].get_perplexity(text)
        return None