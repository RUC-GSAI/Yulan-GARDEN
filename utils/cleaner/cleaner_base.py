import re

class CleanerBase():
    '''
    The Base Class of Each Cleaner Operator, to regularize the functions of each subclass.

    Attributes:
        - no attribute for base class `CleanerBase()`
    '''
    def __init__(self) -> None:
        pass

    def clean_single_text(self, text: str) -> str:
        return text
    
    def _rm_text(self, text: str, rm_str: str) -> str:
        '''
        remove the 'rm_str' in the text
        '''
        return text.replace(rm_str, '')
    
    def _sub_re(self, text: str, re_text, repl_text: str) -> str:
        '''
        're_text' is substituted with 'repl_text'
        '''
        return re.sub(pattern=re_text, repl=repl_text, string=text)