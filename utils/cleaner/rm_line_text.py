import numpy as np
from utils.cleaner.cleaner_base import CleanerBase

class CleanerRemoveLineByText(CleanerBase):
    def __init__(self):
        super().__init__()
    
    def clean_single_text(self, text: str, str_lines: list) -> str:
        '''
        remove the line including any of string in list 'str_lines'
        '''
        lines = text.split('\n')
        flags = np.ones(len(lines))

        for i in range(len(lines)):
            for rule in str_lines:
                flags[i] = flags[i] and (rule not in lines[i])
        
        lines = [each for idx, each in enumerate(lines) if flags[idx]]
        return '\n'.join(lines)