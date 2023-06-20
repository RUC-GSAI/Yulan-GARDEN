from utils.settings import *
import re
import numpy as np
import json

class Debugger():
    def __init__(self, setting: Settings=None) -> None:
        self.debug_paras = {}
        self.load_settings(setting=setting)

    def load_settings(self, setting: Settings) -> None:
        self.debug_paras = setting['debug_paras']
        self.debug_report_path = self.debug_paras['debug_report_path']
        self.debug_short_texts = self.debug_paras['debug_short_texts']
        if self.debug_short_texts['use']:
            '''
            'self.short_texts' are distribution of length of texts.
            (default value of 'self.debug_short_texts['length']' is 200)
            The 0th element 'self.short_texts[0]' is unused.
            The xth element 'self.short_texts[x]' means the number of texts with length x.
            The last element 'self.short_texts[200]' means the number of texts with length more than 200 (including 200).
            '''
            self.short_texts = (self.debug_short_texts['length'] + 1) * [0]
        self.debug_non_ch = self.debug_paras['debug_non_ch']
        if self.debug_non_ch['use']:
            '''
            'self.non_ch' are distribution of non-Chinese characters ratio of texts.
            (default value of 'self.debug_non_ch['length']' is 100)
            The 0th element 'self.non_ch[0]' is unused.
            The xth element 'self.non_ch[x]' means the number of texts with non-Chinese characters ratio [x-1%, x%).
            The last element 'self.non_ch[100]' means the number of texts with non-Chinese characters ratio [99%, 100%].
            '''
            self.non_ch = (self.debug_non_ch['length'] + 1) * [0]
        self.debug_short_lines = self.debug_paras['debug_short_lines']
        if self.debug_short_lines['use']:
            '''
            'self.short_lines' are distribution of short lines ratio of texts (similar to 'self.non_ch').
            (default value of 'self.debug_short_lines['length']' is 100)
            '''
            self.short_lines = (self.debug_short_lines['length'] + 1) * [0]

    def debug_params_report(self) -> None:
        '''
        After debug all the texts, 
        output a debug report about different values of changable parameters with different filter ratios.
        '''
        # aggregate sum (non_ch and short_lines are inverse)
        if self.debug_short_texts['use']:
            agg_short_texts = np.cumsum(self.short_texts)
        if self.debug_non_ch['use']:
            agg_non_ch = np.cumsum(self.non_ch[::-1])
        if self.debug_short_lines['use']:
            agg_short_lines = np.cumsum(self.short_lines[::-1])
        # number of total texts
        total_texts = sum(self.short_texts)
        dic_short_texts, dic_non_ch, dic_short_lines = {}, {}, {}
        percentage_short_texts, percentage_non_ch, percentage_short_lines \
            = agg_short_texts / total_texts, agg_non_ch / total_texts, agg_short_lines / total_texts
        for i in range(1, self.debug_short_texts['length'] + 1):
            if percentage_short_texts[i] > 0.01:
                dic_short_texts[i] = '{:.2%}'.format(percentage_short_texts[i])
            if percentage_short_texts[i] == 1:
                break
        for i in range(0, 100):
            if percentage_non_ch[i] > 0.01:
                dic_non_ch['[{}%, {}%)'.format(99-i, 100-i)] = '{:.2%}'.format(percentage_non_ch[i])
            if percentage_non_ch[i] == 1:
                break
        for i in range(0, 100):
            if percentage_short_lines[i] > 0.01:
                dic_short_lines['[{}%, {}%)'.format(99-i, 100-i)] = '{:.2%}'.format(percentage_short_lines[i])
            if percentage_short_lines[i] == 1:
                break
                
        data = {'short_texts': dic_short_texts, 'non_ch': dic_non_ch, 'short_lines': dic_short_lines}
        # write in the debugger log
        '''
        The format of debugger file:
            {
                "parameter name 1": {
                    value of parameter: filter ratio,
                    value of parameter: filter ratio,
                    ...
                    value of parameter: filter ratio
                },
                "parameter name 2": {
                    value of parameter: filter ratio,
                    value of parameter: filter ratio,
                    ...
                    value of parameter: filter ratio
                },
                ...
                "parameter name n": {
                    value of parameter: filter ratio,
                    value of parameter: filter ratio,
                    ...
                    value of parameter: filter ratio
                }
            }
        note: 'value' here can be a integer value or an interval
        '''
        with open(self.debug_report_path, 'w') as fw:
            json.dump(data, fw, indent=4)
        
        
    
    def debug_single_text(self, text: str) -> None:
        '''
        Debug a single text without change the text.
        Only set a simple DATABASE of changable parameters.
        '''
        if self.debug_short_texts['use']:
            self._debug_short_texts(text)
        if self.debug_non_ch['use']:
            self._debug_non_ch(text)
        if self.debug_short_lines['use']:
            self._debug_short_lines(text)

    def _debug_short_texts(self, text: str) -> None:
        '''
        Modify 'self.short_texts' according to the length of the text.
        '''
        text_length = len(text)
        if text_length >= self.debug_short_texts['length']:
            self.short_texts[self.debug_short_texts['length']] += 1
        else:
            self.short_texts[text_length] += 1
    
    def _debug_non_ch(self, text: str) -> None:
        '''
        Modify 'self.self.non_ch' according to the non-Chinese characters ratio of the text
        '''
        non_ch_ratio = len(re.findall(r'[^\u4e00-\u9fa5]|[a-zA-Z0-9]', text)) / len(text)
        # non_ch_ratio is a percentage, non_ch is a label (integer)
        non_ch = int(100 * non_ch_ratio)
        if non_ch >= self.debug_non_ch['length']:
            self.non_ch[self.debug_non_ch['length']] += 1
        else:
            self.non_ch[non_ch] += 1

    def _debug_short_lines(self, text: str) -> None:
        '''
        Modify 'self.self.non_ch' according to the short lines ratio of the text
        '''
        splits = text.split('\n')
        short_lines_ratio = sum([1 for each in splits if len(each) > 0 and (len(re.findall(r'[\u4e00-\u9fa5]', each)) <= 3)]) / len(splits)
        # short_lines_ratio is a percentage, short_lines is a label (integer)
        short_lines = int(100 * short_lines_ratio)
        if short_lines >= self.debug_short_lines['length']:
            self.short_lines[self.debug_short_lines['length']] += 1
        else:
            self.short_lines[short_lines] += 1
