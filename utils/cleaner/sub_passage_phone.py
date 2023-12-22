import re
from utils.rules.regex import *
from utils.cleaner.cleaner_base import CleanerBase

class CleanerSubstitutePassagePhone(CleanerBase):
    def __init__(self):
        super().__init__()
    
    def clean_single_text(self, text: str, repl_text: str = "**MASKED**PHONE**NUMBER**") -> str:
        '''
        The PHONE NUMBER field in {{text}} will be substituted with {{repl_text}}, default replacement text is "**MASKED**PHONE**"

        The default regular expression is REGEX_ZHPHONE.
        '''
        text = self._sub_re(text=text, re_text=REGEX_ZHPHONE, repl_text=repl_text)
        return text