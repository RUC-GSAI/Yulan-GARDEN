import re
from utils.cleaner.cleaner_base import CleanerBase

class CleanerRemoveSegmentByRegExp(CleanerBase):
    def __init__(self):
        super().__init__()
    
    def clean_single_text(self, text: str, re_text: str) -> str:
        '''
        remove the segment after 're_text'
        '''
        match = re.search(re_text, text)
        if match:
            return text[:match.start()]
        else:
            return text