from utils.filter.filter_base import FilterBase
import re

class FilterPassageByDirtyWords(FilterBase):
    '''
    The Subclass of FilterBase class.
    '''
    def __init__(self) -> None:
        pass

    def filter_single_text(self, text: str, words) -> bool:      
        '''
        if the {{text}} has one of the words, 
        return True (filter this text)
        '''
        for word in words:
            if len(re.findall(word, text)) > 0:
                return True
        return False