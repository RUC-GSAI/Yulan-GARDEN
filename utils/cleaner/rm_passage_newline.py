from utils.cleaner.cleaner_base import CleanerBase

class CleanerRemovePassageNewline(CleanerBase):
    def __init__(self):
        super().__init__()
    
    def clean_single_text(self, text: str) -> str:
        '''
        remove consecutive newlines in the text
        '''
        # strip each line
        # text = '\n'.join([line for line in text.split('\n') if line.strip()])
        patterns = [r'[ |\t]+\n', r'\\n']
        # produce consecutive newlines
        for pattern in patterns:
            text = self._sub_re(text, pattern, '\n')
        # remove consecutive newlines
        text = self._sub_re(text, r'\n{2,}', '\n')
        return text