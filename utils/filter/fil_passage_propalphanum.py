from utils.filter.filter_base import FilterBase
import re

from utils.rules.regex import REGEX_ALPHANUM

class FilterPassageByProportionOfAlphaNumber(FilterBase):
    '''
    The Subclass of FilterBase class.
    '''
    def __init__(self) -> None:
        pass

    def filter_single_text(self, text: str, lower_bound: float, upper_bound: float) -> bool:
        '''
        if the ratio of alpha and number characters more than 'non_ch', 
        return True (filter this text)
        '''
        find = re.findall(REGEX_ALPHANUM, text)                
        prop_alphanum = len(find) / (len(text) + 1e-6)
        return lower_bound >= prop_alphanum or prop_alphanum >= upper_bound