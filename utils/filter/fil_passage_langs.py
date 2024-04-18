from utils.filter.filter_base import FilterBase
from utils.evaluator import LangIdentifier
import re

class FilterPassageByLangs(FilterBase):
    '''
    The Subclass of FilterBase class.
    '''
    def __init__(self) -> None:
        self.language_identifier = LangIdentifier(
            model_path="utils/models/fasttext/lid.176.bin"
        )
        # used in ccnet to filter common crawl
        self.reject_threshold = 0.5
        self.reject_cnt = 0
        self.accept_cnt = 0

    def filter_single_text(self, text: str, accept_lang_list: list) -> bool:      
        '''
        if the language score of {{text}} less than {{reject_threshold}}, then filter it
        '''      
        labels, scores = self.language_identifier.evaluate_single_text(text)
        if all(score < self.reject_threshold for score in scores):
            # uk means "unknown"
            labels = ["uk"]

        accept_lang_list = [each.lower() for each in accept_lang_list]
        if labels[0] not in accept_lang_list:
            self.reject_cnt += 1
            return True
        
        self.accept_cnt += 1
        return False