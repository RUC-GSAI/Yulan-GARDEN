import re
from utils.rules.regex import *
from utils.cleaner.cleaner_base import CleanerBase

class CleanerSubstitutePassageIP(CleanerBase):
    def __init__(self):
        super().__init__()
    
    def clean_single_text(self, text: str, repl_text: str = "**MASKED**IP**") -> str:
        '''
        The IP field in {{text}} will be substituted with {{repl_text}}, default replacement text is "**MASKED**IP**"

        The default regular expression is REGEX_IPV4 and REGEX_IPV6.
        '''
        text = self._sub_re(text=text, re_text=REGEX_IPV4, repl_text=repl_text)
        text = self._sub_re(text=text, re_text=REGEX_IPV6, repl_text=repl_text)
        return text