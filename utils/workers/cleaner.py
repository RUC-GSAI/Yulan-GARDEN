from utils.settings import *
from utils.utils.my_funcs import *
import re
import numpy as np
from zhconv import convert

class Cleaner:
    def __init__(self, setting: Settings=None) -> None:
        self.clean_setting = {}
        self.load_settings(setting=setting)

    def load_settings(self, setting: Settings) -> None:
        self.clean_setting = setting['clean_paras']
        self.my_funcs = self.clean_setting['my_funcs']
        self.rm_crawlerchars = self.clean_setting['rm_crawlerchars']
        self.sub_newline = self.clean_setting['sub_newline']
        self.rm_re_rules = self.clean_setting['rm_re_rules']['re_list'] if self.clean_setting['rm_re_rules']['use'] else []
        self.sub_re_rules = self.clean_setting['sub_re_rules']['re_dict'] if self.clean_setting['sub_re_rules']['use'] else dict()
        self.rm_str_rules = self.clean_setting['rm_str_rules']['str_list'] if self.clean_setting['rm_str_rules']['use'] else []
        self.rm_re_lines = self.clean_setting['rm_re_lines']['re_list'] if self.clean_setting['rm_re_lines']['use'] else []
        self.rm_str_lines = self.clean_setting['rm_str_lines']['str_list'] if self.clean_setting['rm_str_lines']['use'] else []
        self.rm_str_seg = self.clean_setting['rm_str_seg']['str_list'] if self.clean_setting['rm_str_seg']['use'] else []
        self.tra2sim = self.clean_setting['tra2sim']

    def clean_single_text(self, text: str) -> str:
        if self.my_funcs['use']:
            text = self._my_funcs(text, self.my_funcs['funcs'])
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
        if len(self.rm_str_seg) > 0:
            for rm_str in self.rm_str_seg:
                text = self._rm_str_seg(text, rm_str)
        if len(self.rm_str_lines) > 0:
            text = self._rm_lines_str(text, self.rm_str_lines)
        if len(self.rm_re_lines) > 0:
            text = self._rm_lines_re(text, self.rm_re_lines)
        if self.tra2sim['use']:
            target = self.tra2sim['target']
            text = self._tra2sim(text, target)
        if self.sub_newline['use']:
            text = self._sub_newline(text)
        return text    

    def _my_funcs(self, text: str, funcs) -> str:
        '''
        clean the text according to the functions in funcs
        '''
        for func in funcs:
            text = eval(func)(text)
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
    
    def _rm_lines_str(self, text: str, str_lines: list) -> str:
        '''
        remove the line including any of string in list 'str_lines'
        '''
        lines = text.split('\n')
        flags = np.ones(len(lines))

        for i in range(len(lines)):
            for rule in str_lines:
                flags[i] = flags[i] and (rule not in lines[i])
        
        lines = [each for idx, each in enumerate(lines) if flags[idx]]
        return '\n'.join(lines)

    def _rm_lines_re(self, text: str, re_lines: list) -> str:
        '''
        remove the line including 're_line'
        '''
        lines = text.split('\n')
        flags = np.ones(len(lines))

        for i in range(len(lines)):
            for rule in re_lines:
                flags[i] = flags[i] and (re.search(pattern=rule, string=text) is None)
        
        lines = [each for idx, each in enumerate(lines) if flags[idx]]
        return '\n'.join(lines)
    
    def _rm_str_seg(self, text: str, rm_str: list) -> str:
        '''
        remove the segment after 'rm_str'
        '''
        tmp = text.find(rm_str)
        if tmp != -1:
            return text[0:tmp]
        else:
            return text        

    def _rm_crawlerchars(self, text: str) -> str:
        '''
        remove the unused patterns in the text
        \u0020: space
        \u00a0: no-break space
        \u00ad: soft-hyphen
        \u180e: mongolian vowel separator
        \u2000-\u200f: invisible 
        '''
        patterns = ['\b', '\u034f', '\u061c', '\u115f', '\u1160', '\u17b4', '\u17b5', 
                    '\xa0', '\u3000', '\u2800', '&nbsp', '$nbsp']
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
