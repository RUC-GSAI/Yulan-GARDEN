from utils.cleaner.cleaner_base import CleanerBase
from utils.utils.my_funcs import *

class CleanerSubstitutePassageBySelfDefinedFunctions(CleanerBase):
    def __init__(self):
        super().__init__()
    
    def clean_single_text(self, text: str, funcs) -> str:
        '''
        clean the text according to the functions in funcs
        '''
        for func in funcs:
            text = eval(func)(text)
        return text