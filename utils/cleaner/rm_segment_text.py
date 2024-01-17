from utils.cleaner.cleaner_base import CleanerBase

class CleanerRemoveSegmentByText(CleanerBase):
    def __init__(self):
        super().__init__()
    
    def clean_single_text(self, text: str, rm_str: str) -> str:
        '''
        remove the segment after 'rm_str'
        '''
        tmp = text.find(rm_str)
        if tmp != -1:
            return text[0:tmp]
        else:
            return text