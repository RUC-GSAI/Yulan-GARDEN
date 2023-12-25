from utils.filter.filter_base import FilterBase
import re

class FilterPassageByLength(FilterBase):
    '''
    The Subclass of FilterBase class.
    '''
    def __init__(self) -> None:
        pass

    def filter_single_text(self, text: str, min_len: float) -> bool:
        '''
        if the length of {{text}} smaller than {{min_len}}, 
        return True (filter this text)
        '''
        return len(text) < min_len