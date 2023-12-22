from utils.cleaner.cleaner_base import CleanerBase
from zhconv import convert

class CleanerSubstitutePassageSimplifiedChinese(CleanerBase):
    def __init__(self):
        super().__init__()
    
    def clean_single_text(self, text: str, target: str="zh-cn") -> str:
        '''
        traditional characters to their simplified versions
        '''
        text = convert(text, target)
        return text