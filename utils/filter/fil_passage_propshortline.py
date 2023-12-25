from utils.filter.filter_base import FilterBase
import re
from utils.rules.regex import REGEX_ZHCHARALPHANUM

class FilterPassageByProportionofShortline(FilterBase):
    '''
    The Subclass of FilterBase class.
    '''
    def __init__(self) -> None:
        pass

    def filter_single_text(self, text: str, threshold: float, lower_bound: int = 3) -> bool:
        '''
        if the ratio of short line (less than {{lower_bound}} words) more than {{threshold}},
        return True (filter this text)

        Author: @Emanual20
        Last Modified: 2023/11/22
        Modified Target: Laplace Smooth by 1e-6 to solve edge case if 'divided by zero' 
        '''   
        splits = text.split('\n')
        res = sum([1 for each in splits if len(each) > 0 and (len(re.findall(REGEX_ZHCHARALPHANUM, each)) <= lower_bound)]) / (len(splits) + 1e-6)
        return res > threshold