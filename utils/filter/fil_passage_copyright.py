from utils.filter.filter_base import FilterBase
import re

class FilterPassageByCopyright(FilterBase):
    '''
    The Subclass of FilterBase class.
    '''
    def __init__(self) -> None:
        pass

    def filter_single_text(self, text: str, word: str) -> bool:      
        '''
        if the {{word}} exists in text, (case-insensitive)
        return True (filter this text)
        '''      
        return re.search(word, text, re.I)