import re
from utils.cleaner.cleaner_base import CleanerBase

class CleanerRemovePassageText(CleanerBase):
    def __init__(self):
        super().__init__()
    
    def clean_single_text(self, text: str, rm_str: str) -> str:
        '''
        remove the 'rm_str' in the text
        '''
        return self._rm_text(text=text, rm_str=rm_str)