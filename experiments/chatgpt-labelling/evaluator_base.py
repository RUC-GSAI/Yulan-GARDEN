import os

class EvaluatorBase():
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

        - evaluate_single_pair(text1: str, text2: str, lang: str, model: str):
            ** Usage
            Compare a pair of text according to the text quality metric of model.
            ** Params
            @text1: the first text
            @text2: the second text
            @lang: the indicated language
            @model: the model to compare the text quality between text1 and text2

        - evaluate_pairwise_pairs(text_pair_lis: list):
            ** Usage
            Compare multiple pairs of text according to the text quality metric of each subclass of evaluator;
            
            ** Params
            @text_pair_lis(list): the list to be evaluated, each element in this list contain columns "text1", "text2" at least
            @output_path(list): the output path of result file.
            
            ** Return Values
            No return values, but output the result into disk files.
    '''
    def __init__(self) -> None:
        self.input_path = ""
        self.output_path = ""

    def _now_timestamp(self) -> int:
        from datetime import datetime
        return int(datetime.now().timestamp())

    def evaluate_single_text(self, text: str) -> float:
        return 1.0

    def evaluate_single_pair(self, text1: str, text2: str, lang: str, model: str) -> int:
        return -1
    
    def evaluate_pairwise_pairs(self, text_pair_lis: list, input_path: str = "", output_path: str = "") -> None:
        if input_path:
            if not os.path.exists(input_path):
                print("input path not exists")
        if output_path:
            self.output_path = output_path