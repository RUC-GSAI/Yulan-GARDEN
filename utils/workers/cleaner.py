from utils.settings import *
import re
from zhconv import convert

class Cleaner:
    def __init__(self, setting: Settings=None) -> None:
        self.clean_setting = {}
        self.load_settings(setting=setting)

    def load_settings(self, setting: Settings) -> None:
        self.clean_setting = setting['clean_paras']
        self.rm_crawlerchars = self.clean_setting['rm_crawlerchars']
        self.sub_newline = self.clean_setting['sub_newline']
        self.rm_re_rules = self.clean_setting['rm_re_rules']['re_list'] if self.clean_setting['rm_re_rules']['use'] else []
        self.sub_re_rules = self.clean_setting['sub_re_rules']['re_dict'] if self.clean_setting['sub_re_rules']['use'] else dict()
        self.rm_str_rules = self.clean_setting['rm_str_rules']['str_list'] if self.clean_setting['rm_str_rules']['use'] else []
        self.tra2sim = self.clean_setting['tra2sim']

    def clean_single_text(self, text: str) -> str:
        if self.rm_crawlerchars['use']:
            text = self._rm_crawlerchars(text)
        if self.sub_newline['use']:
            text = self._sub_newline(text)
        if len(self.rm_re_rules) > 0:
            for rm_re in self.rm_re_rules:
                text = self._rm_re(text, rm_re)
        if len(self.sub_re_rules) > 0:
            for sub_re, repl_text in self.sub_re_rules.items():
                text = self._sub_re(text, sub_re, repl_text)
        if len(self.rm_str_rules) > 0:
            for rm_str in self.rm_str_rules:
                text = self._rm_text(text, rm_str)
        if self.tra2sim['use']:
            target = self.tra2sim['target']
            text = self._tra2sim(text, target)
        return text    

    def _rm_re(self, text: str, re_text) -> str:
        '''
        remove the 're_text' in the text
        '''
        return re.sub(pattern=re_text, repl='', string=text)

    def _rm_text(self, text: str, rm_str: str) -> str:
        '''
        remove the 'rm_str' in the text
        '''
        return text.replace(rm_str, '')
    
    def _sub_re(self, text: str, re_text, repl_text: str) -> str:
        '''
        're_text' is substituted with 'repl_text'
        '''
        return re.sub(pattern=re_text, repl=repl_text, string=text)

    def _rm_crawlerchars(self, text: str) -> str:
        '''
        remove the unused patterns in the text
        '''
        patterns = ['\xa0', '\u3000', '&nbsp']
        for pattern in patterns:
            text = self._rm_text(text, pattern)
        return text
    
    def _sub_newline(self, text: str) -> str:
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
    
    def _tra2sim(self, text: str, target: str="zh-cn") -> str:
        '''
        traditional characters to their simplified versions
        '''
        text = convert(text, target)
        return text
