import re
from utils.cleaner.cleaner_base import CleanerBase

class CleanerRemovePassageRegExp(CleanerBase):
    def __init__(self):
        super().__init__()
    
    def clean_single_text(self, text: str, re_text) -> str:
        '''
        remove the 're_text' in the text
        '''
        return re.sub(pattern=re_text, repl='', string=text)