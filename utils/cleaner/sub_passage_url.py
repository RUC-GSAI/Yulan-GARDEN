import re
from utils.rules.regex import *
from utils.cleaner.cleaner_base import CleanerBase

class CleanerSubstitutePassageURL(CleanerBase):
    def __init__(self):
        super().__init__()
    
    def clean_single_text(self, text: str, repl_text: str = "**MASKED**URL**") -> str:
        '''
        The URL field in {{text}} will be substituted with {{repl_text}}, default replacement text is "**MASKED**URL**"

        The default regular expression is REGEX_URL.
        '''
        return self._sub_re(text=text, re_text=REGEX_URL, repl_text=repl_text)