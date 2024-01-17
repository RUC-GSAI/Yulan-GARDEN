from utils.cleaner.cleaner_base import CleanerBase

class CleanerRemovePassageInvisbleChars(CleanerBase):
    def __init__(self):
        super().__init__()
    
    def clean_single_text(self, text: str) -> str:
        '''
        remove the unused patterns in the text
        \u0020: space
        \u00a0: no-break space
        \u00ad: soft-hyphen
        \u180e: mongolian vowel separator
        \u2000-\u200f: invisible 
        '''
        patterns = ['\b', '\u034f', '\u061c', '\u115f', '\u1160', '\u17b4', '\u17b5', 
                    '\xa0', '\u3000', '\u2800', '&nbsp', '$nbsp', '&gt;']
        for pattern in patterns:
            text = self._rm_text(text, pattern)

        patterns = [r'[\u0000-\u0009]',
                    r'[\u000e-\u001f]' 
                    r'[\u2400-\u243f]'
                    ]
        for pattern in patterns:
            text = self._sub_re(text, pattern, '')

        patterns = ['\u0020', '\u00a0', '\u00ad', '\u180e', 
                    r'[\u2000-\u200f]', 
                    r'[\u2028-\u202f]',
                    r'[\u205f-\u206e]',
                    '\ufeff']
        for pattern in patterns:
            text = self._sub_re(text, pattern, ' ')

        return text