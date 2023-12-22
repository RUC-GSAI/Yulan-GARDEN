import re
from utils.rules.regex import *
from utils.cleaner.cleaner_base import CleanerBase

class CleanerSubstitutePassageEmail(CleanerBase):
    def __init__(self):
        super().__init__()
    
    def clean_single_text(self, text: str, repl_text: str = "**MASKED**EMAIL**") -> str:
        '''
        The EMAIL field in {{text}} will be substituted with {{repl_text}}, default replacement text is "**MASKED**EMAIL**"

        The default regular expression is REGEX_EMAIL.
        '''
        return self._sub_re(text=text, re_text=REGEX_EMAIL, repl_text=repl_text)