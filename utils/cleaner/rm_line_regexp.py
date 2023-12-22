import numpy as np
import re
from utils.cleaner.cleaner_base import CleanerBase

class CleanerRemoveLineByRegExp(CleanerBase):
    def __init__(self):
        super().__init__()
    
    def clean_single_text(self, text: str, re_lines: list) -> str:
        '''
        remove the line including 're_line'
        '''
        lines = text.split('\n')
        flags = np.ones(len(lines))

        for i in range(len(lines)):
            for rule in re_lines:
                flags[i] = flags[i] and (re.search(pattern=rule, string=text) is None)
        
        lines = [each for idx, each in enumerate(lines) if flags[idx]]
        return '\n'.join(lines)