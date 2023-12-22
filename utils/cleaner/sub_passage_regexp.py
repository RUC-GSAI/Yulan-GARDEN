import re
from utils.cleaner.cleaner_base import CleanerBase

class CleanerSubstitutePassageRegExp(CleanerBase):
    def __init__(self):
        super().__init__()
    
    def clean_single_text(self, text: str, re_text, repl_text: str) -> str:
        '''
        're_text' is substituted with 'repl_text'
        '''
        return self._sub_re(text=text, re_text=re_text, repl_text=repl_text)