from utils.filter.filter_base import FilterBase
import re

class FilterPassageByProportionOfNonChineseChars(FilterBase):
    '''
    The Subclass of FilterBase class.
    '''
    def __init__(self) -> None:
        pass

    def filter_single_text(self, text: str, non_ch: float) -> bool:
        '''
        if the ratio of non Chinese characters more than {{non_ch}}, 
        return True (filter this text)

        Author: @Emanual20
        Last Modified: 2023/11/22
        Modified Target: Laplace Smooth by 1e-6 to solve edge case if 'divided by zero' 
        '''
        find = re.findall(r'[^\u4e00-\u9fa5]|[a-zA-Z0-9]', text)
        return len(find) / (len(text) + 1e-6) >= non_ch