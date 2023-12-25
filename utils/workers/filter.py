from utils.filter import *
from utils.settings import *
from utils.utils.my_rules import *
import re

class Filter:
    def __init__(self, setting: Settings=None) -> None:
        self.filter_setting = {}
        self.load_settings(setting=setting)
        self.num = 0
        self.filter_ops = {
            "FilterPassageByCopyright": FilterPassageByCopyright(),
            "FilterPassageByDirtyWords": FilterPassageByDirtyWords(),
            "FilterPassageByLength": FilterPassageByLength(),
            "FilterPassageByProportionOfAlphaNumber": FilterPassageByProportionOfAlphaNumber(),
            "FilterPassageByProportionOfNonChineseChars": FilterPassageByProportionOfNonChineseChars(),
            "FilterPassageByProportionofShortline": FilterPassageByProportionofShortline(),
            "FilterPassageBySelfDefinedFunctions": FilterPassageBySelfDefinedFunctions()
        }

    def load_settings(self, setting: Settings) -> None:
        self.filter_setting = setting['filter_paras']

        self.fil_my_rules = self.filter_setting['fil_my_rules']
        self.fil_dirty_words = self.filter_setting['fil_dirty_words']
        self.fil_short_texts = self.filter_setting['fil_short_texts']
        self.fil_non_ch = self.filter_setting['fil_non_ch']
        self.fil_alphanum = self.filter_setting['fil_alphanum']
        self.fil_copyright = self.filter_setting['fil_copyright']
        self.fil_short_lines = self.filter_setting['fil_short_lines']
        
    
    def filter_single_text(self, text: str, outInfo: bool=False) -> bool:
        '''
        if single text should be filtered (i.e. scattered),
        return True 
        '''       
        if self.fil_my_rules['use']:
            if self.filter_ops["FilterPassageBySelfDefinedFunctions"].filter_single_text(
                text, 
                self.fil_my_rules['rules']
            ):
                return True

        if self.fil_dirty_words['use']:
            if self.filter_ops["FilterPassageByDirtyWords"].filter_single_text(
                text, 
                self.fil_dirty_words['words']
            ):
                return True
            
        if self.fil_short_texts['use']:
            if self.filter_ops["FilterPassageByLength"].filter_single_text(
                text, 
                self.fil_short_texts['param']
            ):
                return True
            
        if self.fil_non_ch['use']:
            if self.filter_ops["FilterPassageByProportionOfNonChineseChars"].filter_single_text(
                text, 
                self.fil_non_ch['param']
            ):
                return True
        
        if self.fil_alphanum['use']:
            if self.filter_ops['FilterPassageByProportionOfAlphaNumber'].filter_single_text(
                text, 
                self.fil_alphanum['lower_bound'],
                self.fil_alphanum['upper_bound']
            ):
                return True

        if self.fil_copyright['use']:
            for word in self.fil_copyright['en_list']:
                if self.filter_ops["FilterPassageByCopyright"].filter_single_text(
                    text, 
                    word
                ):
                    return True
        
        if self.fil_short_lines['use']:
            if self.filter_ops["FilterPassageByProportionofShortline"].filter_single_text(
                    text, 
                    threshold=self.fil_short_lines['param'], 
                    lower_bound=self.fil_short_lines['lower_bound']
            ):
                return True       
        return False