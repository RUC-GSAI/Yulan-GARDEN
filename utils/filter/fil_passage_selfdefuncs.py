from utils.filter.filter_base import FilterBase
from utils.utils.my_rules import *
import re

class FilterPassageBySelfDefinedFunctions(FilterBase):
    '''
    The Base Class of Each Filter Operator, to regularize the functions of each subclass.

    Attributes:
        - no attribute for base class `FilterBase()`
    '''
    def __init__(self) -> None:
        pass

    def filter_single_text(self, text: str, rules) -> bool:
        '''
        filter the {{text}} according to the rules in {{rules}}
        '''
        for rule in rules:
            if eval(rule)(text):
                return True
        return False