import re

class FilterBase():
    '''
    The Base Class of Each Filter Operator, to regularize the functions of each subclass.

    Attributes:
        - no attribute for base class `FilterBase()`
    '''
    def __init__(self) -> None:
        pass

    def filter_single_text(self, text: str) -> bool:
        return True