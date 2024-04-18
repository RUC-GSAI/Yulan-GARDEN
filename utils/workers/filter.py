from utils.filter import *
from utils.settings import *
from utils.utils.my_rules import *
import os

class Filter:
    def __init__(self, setting: Settings=None) -> None:
        self.filter_setting = {}
        self.num = 0
        
        if setting:
            self.load_settings(setting=setting)
            self.filter_ops = {
                "FilterPassageByCopyright": FilterPassageByCopyright(),
                "FilterPassageByDirtyWords": FilterPassageByDirtyWords(),
                "FilterPassageByLangs": FilterPassageByLangs(),
                "FilterPassageByLangScore": FilterPassageByLangScore(),
                "FilterPassageByLength": FilterPassageByLength(),
                # ppl need a parameter {{input_path}} to initialize
                "FilterPassageByPPL": FilterPassageByPPL(self.input_path, os.path.join(self.output_path, 'sample.jsonl'), os.path.join(self.output_path, 'bound.json'), self.fil_ppl['param']),
                "FilterPassageByProportionOfAlphaNumber": FilterPassageByProportionOfAlphaNumber(),
                "FilterPassageByProportionOfNonChineseChars": FilterPassageByProportionOfNonChineseChars(),
                "FilterPassageByProportionofShortline": FilterPassageByProportionofShortline(),
                "FilterPassageBySelfDefinedFunctions": FilterPassageBySelfDefinedFunctions()
            }

    def load_settings(self, setting: Settings) -> None:
        self.if_filter = setting.get('if_filter', False)
        self.input_path = setting['input_path']
        self.output_path = setting['output_path']
        self.filter_setting = setting['filter_paras']

        self.fil_my_rules = self.filter_setting['fil_my_rules']
        self.fil_dirty_words = self.filter_setting['fil_dirty_words']
        self.fil_langs = self.filter_setting['fil_langs']
        self.fil_lang_score = self.filter_setting['fil_lang_score']
        self.fil_ppl = self.filter_setting['fil_ppl']
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

        # if self.if_filter == False, then do not filter, just return False
        if not self.if_filter:
            return False

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
            
        if self.fil_langs['use']:
            if self.filter_ops["FilterPassageByLangs"].filter_single_text(
                text, 
                accept_lang_list=self.fil_langs['accept_lang_list']
            ):
                return True
        
        if self.fil_ppl['use']:
            if self.filter_ops["FilterPassageByPPL"].filter_single_text(
                text
            ):
                return True

        if self.fil_lang_score['use']:
            if self.filter_ops["FilterPassageByLangScore"].filter_single_text(
                text, 
                reject_threshold=self.fil_lang_score['reject_threshold']
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