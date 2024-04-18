from utils.filter.filter_base import FilterBase
from utils.evaluator import LangIdentifier
import re

class FilterPassageByLangScore(FilterBase):
    '''
    The Subclass of FilterBase class.
    '''
    def __init__(self) -> None:
        self.language_identifier = LangIdentifier(
            model_path="utils/models/fasttext/lid.176.bin"
        )
        self.reject_cnt = 0
        self.accept_cnt = 0

    def filter_single_text(self, text: str, reject_threshold: float = 0.5) -> bool:      
        '''
        if the language score of {{text}} less than {{reject_threshold}}, then filter it
        '''      
        labels, scores = self.language_identifier.evaluate_single_text(text)
        if all(score < reject_threshold for score in scores):
            # uk means "unknown"
            labels = ["uk"]
            self.reject_cnt += 1
            return True
        
        self.accept_cnt += 1
        return False