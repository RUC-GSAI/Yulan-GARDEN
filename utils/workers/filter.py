from utils.settings import *
import re

class Filter:
    def __init__(self, setting: Settings=None) -> None:
        self.filter_setting = {}
        self.load_settings(setting=setting)

    def load_settings(self, setting: Settings) -> None:
        self.filter_setting = setting['filter_paras']
        self.fil_short_texts = self.filter_setting['fil_short_texts']
        self.fil_non_ch = self.filter_setting['fil_non_ch']
        self.fil_copyright = self.filter_setting['fil_copyright']
        self.fil_short_lines = self.filter_setting['fil_short_lines']
    

    def filter_single_text(self, text: str, outInfo: bool=False) -> bool:
        '''
        if single text should be filtered (i.e. scattered),
        return True 
        '''       
        if self.fil_short_texts['use']:
            if self._fil_short_texts(text, self.fil_short_texts['param']):
                if outInfo:
                    print('The text is too short.')
                return True
        if self.fil_non_ch['use']:
            if self._fil_non_ch(text, self.fil_non_ch['param']):
                if outInfo:
                    print('Too many non-Chinese characters.')
                return True
        
        if self.fil_copyright['use']:
            for word in self.fil_copyright['ch_list']:
                if self._fil_copyright_ch(text, word):
                    if outInfo:
                        print('Chinese copyright.')
                    return True
            for word in self.fil_copyright['en_list']:
                if self._fil_copyright_en(text, word):
                    if outInfo:
                        print('English copyright.')
                    return True
        
        if self.fil_short_lines['use']:
            if self._fil_short_lines(text, self.fil_short_lines['param']):
                if outInfo:
                    print('Too many short lines.')
                return True
        
        return False

    
    def _fil_short_texts(self, text: str, min_len: float) -> bool:
        '''
        if the length of text smaller than 'min_len', 
        return True (filter this text)
        '''
        return len(text) < min_len
    
    def _fil_non_ch(self, text: str, non_ch: float) -> bool:
        '''
        if the ratio of non Chinese characters more than 'non_ch', 
        return True (filter this text)
        '''
        find = re.findall(r'[^\u4e00-\u9fa5]|[a-zA-Z0-9]', text)                
        return len(find) / len(text) >= non_ch
    
    def _fil_copyright_ch(self, text: str, word: str) -> bool:      
        '''
        if the Chinese 'word' exists in text, 
        return True (filter this text)
        '''     
        return re.search(word, text)
    
    def _fil_copyright_en(self, text: str, word: str) -> bool:      
        '''
        if the English 'word' exists in text, (case-insensitive)
        return True (filter this text)
        '''      
        return re.search(word, text, re.I)

    def _fil_short_lines(self, text: str, threshold: float) -> bool:
        '''
        if the ratio of short line (less than 3 words) more than 'threshold',
        return True (filter this text)
        '''   
        splits = text.split('\n')
        res = sum([1 for each in splits if len(each) > 0 and (len(re.findall(r'[\u4e00-\u9fa5]', each)) <= 3)]) / len(splits)
        return res > threshold
        


        