from utils.settings import *
import re
import numpy as np
import json
import time
from datetime import datetime

def log_text(text: str, desc: str="LOG"):
    print(f"[{desc}, {datetime.now()}]: ", text)

class Debugger():
    def __init__(self, setting: Settings=None) -> None:
        self.load_settings(setting=setting)
        self.total_texts = 0

    def load_settings(self, setting: Settings) -> None:
        # for filter parameters
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
            The 0th element 'self.non_ch[0]' is unused.
            The xth element 'self.non_ch[x]' means the number of texts with non-Chinese characters ratio [x-1%, x%).
            The last element 'self.non_ch[100]' means the number of texts with non-Chinese characters ratio [99%, 100%].
            '''
            self.non_ch = (100 + 1) * [0]
        self.debug_short_lines = self.debug_paras['debug_short_lines']
        if self.debug_short_lines['use']:
            '''
            'self.short_lines' are distribution of short lines ratio of texts (similar to 'self.non_ch').
            '''
            self.short_lines = (100 + 1) * [0]
        
        # for cleaner 
        self.clean_setting = setting['clean_paras']
        if self.clean_setting['rm_re_rules']['use']:
            self.debug_rm_re_rules = self.clean_setting['rm_re_rules']['re_list']
            '''
            'self.rm_re_rules' is a dict including 3 parts:
                'match ratio': the percentage of matching ratio (matching times / total texts)
                'avg time': the average execute time (sum of execute time / total texts)
                'cases': some matching examples
            '''
            self.rm_re_rules = {}
            for rule in self.debug_rm_re_rules:
                self.rm_re_rules[rule] = {'match ratio': 0, 'avg time': 0, 'cases': []}
        if self.clean_setting['sub_re_rules']['use']:
            self.debug_sub_re_rules = self.clean_setting['sub_re_rules']['re_dict']
            '''
            'self.sub_re_rules' is a dict including 3 parts
            (similar to 'self.rm_re_rules')
            '''
            self.sub_re_rules = {}
            for rule, _ in self.debug_sub_re_rules.items():
                self.sub_re_rules[rule] = {'match ratio': 0, 'avg time': 0, 'cases': []}
        if self.clean_setting['rm_str_rules']['use']:
            self.debug_rm_str_rules = self.clean_setting['rm_str_rules']['str_list']
            '''
            'self.rm_re_rules' is a dict including 2 parts 
            (similar to 'self.rm_re_rules' without 'cases')
            '''
            self.rm_str_rules = {}
            for rule in self.debug_rm_str_rules:
                self.rm_str_rules[rule] = {'match ratio': 0, 'avg time': 0, 'cases': []}

    def debug_params_report(self) -> None:
        '''
        After debug all the texts, 
        output a debug report about different values of changable parameters with different filter ratios.
        '''
        filter_report = self._filter_report()
        cleaner_report = self._cleaner_report()
        report = {"filter report": filter_report, "cleaner report": cleaner_report}
        '''
        The format of debugger file:
        {
            "filter report": {
                "parameter name 1": {
                    "info": "...",
                    "param: filter ratio":{                    
                        value of parameter: filter ratio,
                        value of parameter: filter ratio,
                        ...
                        value of parameter: filter ratio
                    }
                },
                "parameter name 2": {
                    "info": "...",
                    "param: filter ratio":{                    
                        value of parameter: filter ratio,
                        value of parameter: filter ratio,
                        ...
                        value of parameter: filter ratio
                    }
                },
                ...
                "parameter name n": {
                    "info": "...",
                    "param: filter ratio":{                    
                        value of parameter: filter ratio,
                        value of parameter: filter ratio,
                        ...
                        value of parameter: filter ratio
                    }
                },
            }
            "cleaner report": {
                "cleaner type 1": {
                    "rule 1": {
                        "match ratio": "...%",
                        "avg time": "...s",
                        "cases": []
                    },
                    "rule 2": {
                        "match ratio": "...%",
                        "avg time": "...s",
                        "cases": []
                    },
                    ...
                    "rule n": {
                        "match ratio": "...%",
                        "avg time": "...s",
                        "cases": []
                    }
                },
                "cleaner type 2": {
                    "rule 1": {
                        "match ratio": "...%",
                        "avg time": "...s",
                        "cases": []
                    },
                    ...
                },
                ...
            }
        }
        note: 'value' here can be a integer value or an interval
        '''
        with open(self.debug_report_path, 'w', encoding='utf-8') as fw:
            json.dump(report, fw, indent=4, ensure_ascii=False)
    
    def debug_single_text(self, text: str) -> None:
        '''
        Debug a single text without change the text.
        Only set a simple DATABASE of changable parameters.
        '''
        self.total_texts += 1
        if self.debug_short_texts['use']:
            self._debug_short_texts(text)
        if self.debug_non_ch['use']:
            self._debug_non_ch(text)
        if self.debug_short_lines['use']:
            self._debug_short_lines(text)
        if self.clean_setting['rm_re_rules']['use']:
            self._debug_rm_re_rules(text)
        if self.clean_setting['sub_re_rules']['use']:
            self._debug_sub_re_rules(text)
        if self.clean_setting['rm_str_rules']['use']:
            self._debug_rm_str_rules(text)

    def _filter_report(self):
        '''
        generate filter report and return the report
        '''
        # aggregate sum (non_ch and short_lines are inverse)
        if self.debug_short_texts['use']:
            agg_short_texts = np.cumsum(self.short_texts)
        if self.debug_non_ch['use']:
            agg_non_ch = np.cumsum(self.non_ch[::-1])
        if self.debug_short_lines['use']:
            agg_short_lines = np.cumsum(self.short_lines[::-1])

        percentage_short_texts, percentage_non_ch, percentage_short_lines \
            = agg_short_texts / self.total_texts, agg_non_ch / self.total_texts, agg_short_lines / self.total_texts
        # some variables for output report
        dic_short_texts, dic_non_ch, dic_short_lines = {}, {}, {}
        info_short_texts, info_non_ch, info_short_lines = '', '', ''
        # short_texts
        for i in range(1, self.debug_short_texts['length']):
            if percentage_short_texts[i] > 0.01:
                dic_short_texts[i] = '{:.2%}'.format(percentage_short_texts[i])
                if percentage_short_texts[i] == 1:
                    break
        # The last element means the number of texts with length more than the largest number (including it).
        if i == self.debug_short_texts['length'] - 1 and percentage_short_texts[i] < 1:
            i += 1
            dic_short_texts['>={}'.format(i)] = '{:.2%}'.format(percentage_short_texts[i])
            info_short_texts = 'If you want more details about parameter \'short_texts\', please increase the value of settings[\'debug_paras\'][\'debug_short_texts\'][\'length\'] in settings.json.'
        # non_ch
        for i in range(1, 100 + 1):
            if percentage_non_ch[i] > 0.01:
                dic_non_ch['[{}%, {}%)'.format(100-i, 101-i)] = '{:.2%}'.format(percentage_non_ch[i])
                if percentage_non_ch[i] == 1:
                    break
        # short_lines
        for i in range(1, 100 + 1):
            if percentage_short_lines[i] > 0.01:
                dic_short_lines['[{}%, {}%)'.format(100-i, 101-i)] = '{:.2%}'.format(percentage_short_lines[i])
                if percentage_short_lines[i] == 1:
                    break
                
        data = {'short_texts': {'info': info_short_texts, 'param: filter ratio': dic_short_texts}, 'non_ch': {'info': info_non_ch, 'param: filter ratio': dic_non_ch}, 'short_lines': {'info': info_short_lines, 'param: filter ratio': dic_short_lines}}
        return data

    def _cleaner_report(self):
        '''
        generate filter report and return the report
        '''
        if self.clean_setting['rm_re_rules']['use']:
            for rule in self.debug_rm_re_rules:
                self.rm_re_rules[rule]['match ratio'] = '{:.2%}'.format(self.rm_re_rules[rule]['match ratio']/self.total_texts)
                self.rm_re_rules[rule]['avg time'] = '{:.5f} * 10^-4 s'.format(10000*self.rm_re_rules[rule]['avg time']/self.total_texts)
        if self.clean_setting['sub_re_rules']['use']:
            for rule, _ in self.debug_sub_re_rules.items():
                self.sub_re_rules[rule]['match ratio'] = '{:.2%}'.format(self.sub_re_rules[rule]['match ratio']/self.total_texts)
                self.sub_re_rules[rule]['avg time'] = '{:.5f} * 10^-4 s'.format(10000*self.sub_re_rules[rule]['avg time']/self.total_texts)
        if self.clean_setting['rm_str_rules']['use']:
            for rule in self.debug_rm_str_rules:
                self.rm_str_rules[rule]['match ratio'] = '{:.2%}'.format(self.rm_str_rules[rule]['match ratio']/self.total_texts)
                self.rm_str_rules[rule]['avg time'] = '{:.5f} * 10^-4 s'.format(10000*self.rm_str_rules[rule]['avg time']/self.total_texts)
        data = {'rm_re_rules': self.rm_re_rules, 'sub_re_rules': self.sub_re_rules, 'rm_str_rules': self.rm_str_rules}
        return data


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
        Modify 'self.non_ch' according to the non-Chinese characters ratio of the text
        '''
        non_ch_ratio = len(re.findall(r'[^\u4e00-\u9fa5]|[a-zA-Z0-9]', text)) / len(text)
        # non_ch_ratio is a percentage, non_ch is a label (integer)
        non_ch = int(100 * non_ch_ratio)
        if non_ch >= 100:
            self.non_ch[100] += 1
        else:
            self.non_ch[non_ch] += 1

    def _debug_short_lines(self, text: str) -> None:
        '''
        Modify 'self.short_lines' according to the short lines ratio of the text
        '''
        splits = text.split('\n')
        short_lines_ratio = sum([1 for each in splits if len(each) > 0 and (len(re.findall(r'[\u4e00-\u9fa5]', each)) <= 3)]) / len(splits)
        # short_lines_ratio is a percentage, short_lines is a label (integer)
        short_lines = int(100 * short_lines_ratio)
        if short_lines >= 100:
            self.short_lines[100] += 1
        else:
            self.short_lines[short_lines] += 1

    def _debug_rm_re_rules(self, text: str) -> None:
        '''
        Modify 'self.rm_re_rules' according to the matching times, the execute time, matching examples.
        '''
        for rule in self.debug_rm_re_rules:
            # self.rm_re_rules[rule] = {'match ratio': 0, 'avg time': 0, 'cases': []}
            if re.search(pattern=rule, string=text) != None:
                self.rm_re_rules[rule]['match ratio'] += 1
            # start = time.time()
            self.rm_re_rules[rule]['avg time'] -= time.time()
            re.sub(pattern=rule, repl='', string=text)
            # end = time.time()
            self.rm_re_rules[rule]['avg time'] += time.time()

    def _debug_sub_re_rules(self, text: str) -> None:
        '''
        Modify 'self.sub_re_rules' according to the matching times, the execute time, matching examples.
        '''
        for rule, repl in self.debug_sub_re_rules.items():
            # self.sub_re_rules[rule] = {'match ratio': 0, 'avg time': 0, 'cases': []}
            if re.search(pattern=rule, string=text) != None:
                self.sub_re_rules[rule]['match ratio'] += 1
            # start = time.time()
            self.sub_re_rules[rule]['avg time'] -= time.time()
            re.sub(pattern=rule, repl=repl, string=text)
            # end = time.time()
            self.sub_re_rules[rule]['avg time'] += time.time()

    def _debug_rm_str_rules(self, text: str) -> None:
        '''
        Modify 'self.rm_str_rules' according to the matching times, the execute time, matching examples.
        '''
        for rule in self.debug_rm_str_rules:
            # self.rm_str_rules[rule] = {'match ratio': 0, 'avg time': 0, 'cases': []}
            if text.find(rule) != -1:
                self.rm_str_rules[rule]['match ratio'] += 1
            # start = time.time()
            self.rm_str_rules[rule]['avg time'] -= time.time()
            text.replace(rule, '')
            # end = time.time()
            self.rm_str_rules[rule]['avg time'] += time.time()