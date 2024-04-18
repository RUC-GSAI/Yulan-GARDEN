from utils.settings import *
from utils.evaluator.PerplexityEvaluator import PerplexityEvaluator
from utils.evaluator.LangIdentifier import LangIdentifier
import re
import numpy as np
import json
import time
from typing import Union
from statistics import mean, variance
import matplotlib.pyplot as plt
from matplotlib import cm
import os
import seaborn as sns
from shutil import rmtree


def binary_search(array_list: list, find: float, left: int, right: int) -> list:
    '''
    @params:
        'array_list': an ascending order array
        'find': the value to find
        'left': starting left label
        'right': starting right label
    Return:
        []:
            length = 0: do not find
            length = 1: the exact label
            length = 2: the interval
    '''
    if array_list[left] > find or array_list[right] < find:
        return []
    while left < right - 1:
        if array_list[left] == find:
            return [left]
        elif array_list[right] == find:
            return [right]
        else:
            mid = int((left + right) / 2)
            if array_list[mid] == find:
                return [mid]
            elif array_list[mid] > find:
                right = mid
            else:
                left = mid
    return [left, right]

class Debugger():
    def __init__(self, setting: Settings=None, option: str='raw') -> None:
        self.fig_path = f'static/{option}_figs/'
        self.cases_num = 3
        self.total_texts = 0
        self.load_settings(setting=setting)

    def load_settings(self, setting: Settings) -> None:        
        # for filter parameters
        self.debug_paras = setting['debug_paras']
        self.debug_report_path = self.debug_paras['debug_report_path']
        self.debug_short_texts = self.debug_paras['debug_short_texts']
        self.debug_short_texts['use'] = True
        # self.debug_langs = self.debug_paras['debug_langs']
        self.debug_langs = {'use': True}
        self.debug_ppl = self.debug_paras['debug_ppl']
        # 'debug_find_cases' is regarded as a cleaner method
        self.debug_find_cases = self.debug_paras['debug_find_cases']
        if 'debug_cases_num' in self.debug_paras.keys(): self.cases_num = self.debug_paras['debug_cases_num']
        if 'debug_sample_num_per_file' in self.debug_paras.keys(): self.sample_num = self.debug_paras['debug_sample_num_per_file']
        if self.debug_short_texts['use']:
            '''
            'self.short_texts' are distribution of length of texts.
            (default value of 'self.debug_short_texts['length']' is 200)
            The 0th element 'self.short_texts[0]' is unused.
            The xth element 'self.short_texts[x]' means the number of texts with length x.
            The last element 'self.short_texts[200]' means the number of texts with length more than 200 (including 200).
            '''
            self.short_texts = (self.debug_short_texts['length'] + 1) * [0]
            '''
            'self.texts_length' is a list of length of texts. 
            (calculate the mean and the variance, draw the distribution of texts length.)
            '''
            self.texts_length = []
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
        if self.debug_langs['use']:
            # create LangIdentifier to make statistics on the language distribution of text
            self.langidentifier = LangIdentifier()
            '''
            'self.langs' is distribution of language ratio of texts.
            '''
            self.langs = {}
            # ppl must need language
            if self.debug_ppl['use']:
                # create PerplexityEvaluator to make statistics on the ppl distribution of text
                self.perplexityEvaluator = PerplexityEvaluator()
                '''
                'self.ppl' are lists of ppl of texts: {lang: [list of ppl]}
                '''
                self.ppl = {}

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
                self.rm_re_rules[rule] = {'match ratio': 0, 'avg time': 0, 'cases': set()}
        if self.debug_find_cases['use']:
            self.debug_find_cases_words = self.debug_find_cases['words']
            '''
            'self.find_cases_words' is a dict including 3 parts:
                'match ratio': the percentage of matching ratio (matching times / total texts)
                'avg time': the average execute time (sum of execute time / total texts)
                'cases': some matching examples
            '''
            self.find_cases_words = {}
            for word in self.debug_find_cases_words:
                self.find_cases_words[word] = {'match ratio': 0, 'avg time': 0, 'cases': set()}
        if self.clean_setting['sub_re_rules']['use']:
            self.debug_sub_re_rules = self.clean_setting['sub_re_rules']['re_dict']
            '''
            'self.sub_re_rules' is a dict including 3 parts
            (similar to 'self.rm_re_rules')
            '''
            self.sub_re_rules = {}
            for rule, _ in self.debug_sub_re_rules.items():
                self.sub_re_rules[rule] = {'match ratio': 0, 'avg time': 0, 'cases': set()}
        if self.clean_setting['rm_str_rules']['use']:
            self.debug_rm_str_rules = self.clean_setting['rm_str_rules']['str_list']
            '''
            'self.rm_re_rules' is a dict including 2 parts 
            (similar to 'self.rm_re_rules' without 'cases')
            '''
            self.rm_str_rules = {}
            for rule in self.debug_rm_str_rules:
                self.rm_str_rules[rule] = {'match ratio': 0, 'avg time': 0}
        if self.clean_setting['rm_str_seg']['use']:
            self.debug_rm_str_seg = self.clean_setting['rm_str_seg']['str_list']
            '''
            'self.rm_str_seg' is a dict including 3 parts 
            (similar to 'self.rm_re_rules')
            '''
            self.rm_str_seg = {}
            for rule in self.debug_rm_str_seg:
                self.rm_str_seg[rule] = {'match ratio': 0, 'avg time': 0, 'cases': set()}

    def debug_params_report(self) -> Union[dict, None]:
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

        try: 
            return self.ppl
        except AttributeError:
            return None        
    
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
        if self.debug_find_cases['use']:
            self._debug_find_cases(text)
        if self.debug_langs['use']:
            language = self._debug_langs(text)
            if self.debug_ppl['use']:
                self._debug_ppl(text, language)
        if self.clean_setting['rm_re_rules']['use']:
            self._debug_rm_re_rules(text)
        if self.clean_setting['sub_re_rules']['use']:
            self._debug_sub_re_rules(text)
        if self.clean_setting['rm_str_rules']['use']:
            self._debug_rm_str_rules(text)
        if self.clean_setting['rm_str_seg']['use']:
            self._debug_rm_str_seg(text)

    def _filter_report(self):
        '''
        generate filter report and return the report
        '''
        # aggregate sum (non_ch and short_lines are inverse)
        if self.debug_short_texts['use']:
            agg_short_texts = np.cumsum(self.short_texts)
            percentage_short_texts = agg_short_texts / self.total_texts
        if self.debug_non_ch['use']:
            agg_non_ch = np.cumsum(self.non_ch[::-1])
            percentage_non_ch = agg_non_ch / self.total_texts
        if self.debug_short_lines['use']:
            agg_short_lines = np.cumsum(self.short_lines[::-1])
            percentage_short_lines = agg_short_lines / self.total_texts
        if self.debug_langs['use']:
            percentage_lang = {lang: count/self.total_texts for lang, count in self.langs.items()}

        # some variables for output report
        dic_short_texts, dic_non_ch, dic_short_lines, dic_length, dic_langs, dic_ppl = {}, {}, {}, {}, {}, {}
        info_short_texts, info_non_ch, info_short_lines = '', '', ''
        # short_texts
        if self.debug_short_texts['use']:
            # if the user need a fixed filter ratio
            if self.debug_short_texts['if_fix_fil_ratio']:
                # binary search the parameter 
                interval = binary_search(percentage_short_texts, self.debug_short_texts['exp_fil_ratio'], 1, self.debug_short_texts['length'])
                # do not find suitable parameter
                if len(interval) == 0:
                    info_short_texts = 'The expected filter ratio is smaller than 0 or larger than 1!'
                else:
                    for i in interval:
                        dic_short_texts[i] = '{:.2%}'.format(percentage_short_texts[i])
                    if i == self.debug_short_texts['length']:
                        info_short_texts = 'If you want more details about parameter \'short_texts\', please increase the value of settings[\'debug_paras\'][\'debug_short_texts\'][\'length\'] in settings.json.'
            else:
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
        if self.debug_non_ch['use']:
            # if the user need a fixed filter ratio
            if self.debug_non_ch['if_fix_fil_ratio']:
                # binary search the parameter 
                interval = binary_search(percentage_non_ch, self.debug_non_ch['exp_fil_ratio'], 1, 100)
                # do not find suitable parameter
                if len(interval) == 0:
                    info_non_ch = 'The expected filter ratio is smaller than 0 or larger than 1!'
                else:
                    for i in interval:
                        dic_non_ch['[{}%, {}%)'.format(100-i, 101-i)] = '{:.2%}'.format(percentage_non_ch[i])
            else:
                for i in range(1, 100 + 1):
                    if percentage_non_ch[i] > 0.01:
                        dic_non_ch['[{}%, {}%)'.format(100-i, 101-i)] = '{:.2%}'.format(percentage_non_ch[i])
                        if percentage_non_ch[i] == 1:
                            break
        # short_lines
        if self.debug_short_lines['use']:
            # if the user need a fixed filter ratio
            if self.debug_short_lines['if_fix_fil_ratio']:
                # binary search the parameter 
                interval = binary_search(percentage_short_lines, self.debug_short_lines['exp_fil_ratio'], 1, 100)
                # do not find suitable parameter
                if len(interval) == 0:
                    info_short_lines = 'The expected filter ratio is smaller than 0 or larger than 1!'
                else:
                    for i in interval:
                        dic_short_lines['[{}%, {}%)'.format(100-i, 101-i)] = '{:.2%}'.format(percentage_short_lines[i])
            else:
                for i in range(1, 100 + 1):
                    if percentage_short_lines[i] > 0.01:
                        dic_short_lines['[{}%, {}%)'.format(100-i, 101-i)] = '{:.2%}'.format(percentage_short_lines[i])
                        if percentage_short_lines[i] == 1:
                            break

        if self.debug_langs['use']:
            dic_langs = {lang: '{:.2%}'.format(percentage) for lang, percentage in percentage_lang.items()}
            if self.debug_ppl['use']:
                dic_ppl = {}
                for lang, ppl_list in self.ppl.items():
                    if len(ppl_list) > 1:
                        dic_ppl[lang] = {'mean': round(mean(ppl_list), 2), 'var': round(variance(ppl_list), 2)}
                    else:
                        dic_ppl[lang] = {'mean': round(mean(ppl_list), 2), 'var': None}
            if len(self.texts_length) > 1:  
                dic_length = {'mean': round(mean(self.texts_length)), 'var': round(variance(self.texts_length))}
            else:
                dic_length = {'mean': round(mean(self.texts_length)), 'var': None}

        # draw figures
        if os.path.exists(self.fig_path): 
            rmtree(self.fig_path)
        os.makedirs(self.fig_path, exist_ok=True)

        if self.debug_short_texts['use']:
            self._histogram(self.texts_length, os.path.join(self.fig_path, 'lengths.svg'), 'lengths distribution')
        if self.debug_langs['use']:
            self._pie_chart(self.langs, os.path.join(self.fig_path, 'langs.svg'), 'languages distribution')        
            if self.debug_ppl['use']:
                for lang in self.ppl:
                    self._histogram(self.ppl[lang], os.path.join(self.fig_path, 'ppl_{}.svg'.format(lang)), 'ppl of {}'.format(lang))

        data = {'texts_length': dic_length, 'langs': dic_langs, 'ppls': dic_ppl, 'short_texts': {'info': info_short_texts, 'param: filter ratio': dic_short_texts}, 'non_ch': {'info': info_non_ch, 'param: filter ratio': dic_non_ch}, 'short_lines': {'info': info_short_lines, 'param: filter ratio': dic_short_lines}}
        return data

    def _cleaner_report(self):
        '''
        generate filter report and return the report
        '''
        if self.debug_find_cases['use']:
            for word in self.debug_find_cases_words:
                self.find_cases_words[word]['match ratio'] = '{:.2%}'.format(self.find_cases_words[word]['match ratio']/self.total_texts)
                self.find_cases_words[word]['avg time'] = '{:.5f} * 10^-4 s'.format(10000*self.find_cases_words[word]['avg time']/self.total_texts)
        else:
            self.find_cases_words = None
        if self.clean_setting['rm_re_rules']['use']:
            for rule in self.debug_rm_re_rules:
                self.rm_re_rules[rule]['match ratio'] = '{:.2%}'.format(self.rm_re_rules[rule]['match ratio']/self.total_texts)
                self.rm_re_rules[rule]['avg time'] = '{:.5f} * 10^-4 s'.format(10000*self.rm_re_rules[rule]['avg time']/self.total_texts)
        else:
            self.rm_re_rules = None
        if self.clean_setting['sub_re_rules']['use']:
            for rule, _ in self.debug_sub_re_rules.items():
                self.sub_re_rules[rule]['match ratio'] = '{:.2%}'.format(self.sub_re_rules[rule]['match ratio']/self.total_texts)
                self.sub_re_rules[rule]['avg time'] = '{:.5f} * 10^-4 s'.format(10000*self.sub_re_rules[rule]['avg time']/self.total_texts)
        else:
            self.sub_re_rules = None
        if self.clean_setting['rm_str_rules']['use']:
            for rule in self.debug_rm_str_rules:
                self.rm_str_rules[rule]['match ratio'] = '{:.2%}'.format(self.rm_str_rules[rule]['match ratio']/self.total_texts)
                self.rm_str_rules[rule]['avg time'] = '{:.5f} * 10^-4 s'.format(10000*self.rm_str_rules[rule]['avg time']/self.total_texts)
        else:
            self.rm_str_rules = None
        if self.clean_setting['rm_str_seg']['use']:
            for rule in self.debug_rm_str_seg:
                self.rm_str_seg[rule]['match ratio'] = '{:.2%}'.format(self.rm_str_seg[rule]['match ratio']/self.total_texts)
                self.rm_str_seg[rule]['avg time'] = '{:.5f} * 10^-4 s'.format(10000*self.rm_str_seg[rule]['avg time']/self.total_texts)
        else:
            self.rm_str_seg = None

        # Object of type 'set' is not JSON serializable
        if self.debug_find_cases['use']:
            for word in self.debug_find_cases_words:
                self.find_cases_words[word]['cases'] = list(self.find_cases_words[word]['cases'])
        if self.clean_setting['rm_re_rules']['use']:
            for rule in self.debug_rm_re_rules:
                self.rm_re_rules[rule]['cases'] = list(self.rm_re_rules[rule]['cases'])
        if self.clean_setting['sub_re_rules']['use']:
            for rule, _ in self.debug_sub_re_rules.items():
                self.sub_re_rules[rule]['cases'] = list(self.sub_re_rules[rule]['cases'])
        if self.clean_setting['rm_str_seg']['use']:
            for rule in self.debug_rm_str_seg:
                self.rm_str_seg[rule]['cases'] = list(self.rm_str_seg[rule]['cases'])

        
        data = {'find_cases': self.find_cases_words, 'rm_re_rules': self.rm_re_rules, 'sub_re_rules': self.sub_re_rules, 'rm_str_rules': self.rm_str_rules, 'rm_str_seg': self.rm_str_seg}
        return data


    def _debug_short_texts(self, text: str) -> None:
        '''
        Modify 'self.short_texts' and 'self.texts_length' according to the length of the text.
        '''
        text_length = len(text)
        self.texts_length.append(text_length)
        if text_length >= self.debug_short_texts['length']:
            self.short_texts[self.debug_short_texts['length']] += 1
        else:
            self.short_texts[text_length] += 1
    
    def _debug_non_ch(self, text: str) -> None:
        '''
        Modify 'self.non_ch' according to the non-Chinese characters ratio of the text
        '''
        non_ch_ratio = len(re.findall(r'[^\u4e00-\u9fa5]|[a-zA-Z0-9]', text)) / (len(text) + 1e-8)
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
        short_lines_ratio = sum([1 for each in splits if len(each) > 0 and (len(re.findall(r'[\u4e00-\u9fa5]', each)) <= 3)]) / (len(splits) + 1e-8)
        # short_lines_ratio is a percentage, short_lines is a label (integer)
        short_lines = int(100 * short_lines_ratio)
        if short_lines >= 100:
            self.short_lines[100] += 1
        else:
            self.short_lines[short_lines] += 1

    def _debug_langs(self, text: str) -> str:
        '''
        Modify 'self.langs' according to the language of the text
        '''
        label, _ = self.langidentifier.evaluate_single_text(text)
        if label[0] not in self.langs:
            self.langs[label[0]] = 1
        else:
            self.langs[label[0]] += 1
        return label[0]

    def _debug_ppl(self, text: str, lang: str) -> None:
        '''
        Modify 'self.ppl' according to the language and the ppl of the text
        '''
        if lang not in ['en', 'zh']:
            return
        if lang not in self.ppl:
            self.ppl[lang] = []
        ppl = self.perplexityEvaluator.evaluate_single_text(text, lang)
        if ppl:
            self.ppl[lang].append(ppl)
        
    def _debug_find_cases(self, text: str) -> None:
        '''
        Modify 'self.find_cases_words' according to the matching times, the execute time, matching examples.
        '''
        for word in self.debug_find_cases_words:
            re_obj = re.search(pattern=word, string=text)
            if re_obj != None:
                self.find_cases_words[word]['match ratio'] += 1
                if len(self.find_cases_words[word]['cases']) < self.cases_num:
                    self.find_cases_words[word]['cases'].add(text)
            # start = time.time()
            self.find_cases_words[word]['avg time'] -= time.time()
            re.sub(pattern=word, repl='', string=text)
            # end = time.time()
            self.find_cases_words[word]['avg time'] += time.time()

    def _debug_rm_re_rules(self, text: str) -> None:
        '''
        Modify 'self.rm_re_rules' according to the matching times, the execute time, matching examples.
        '''
        for rule in self.debug_rm_re_rules:
            # self.rm_re_rules[rule] = {'match ratio': 0, 'avg time': 0, 'cases': []}
            re_obj = re.search(pattern=rule, string=text)
            if re_obj != None:
                self.rm_re_rules[rule]['match ratio'] += 1
                if len(self.rm_re_rules[rule]['cases']) < self.cases_num:
                    self.rm_re_rules[rule]['cases'].add(re_obj.group())
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
            re_obj = re.search(pattern=rule, string=text)
            if re_obj != None:
                self.sub_re_rules[rule]['match ratio'] += 1
                if len(self.sub_re_rules[rule]['cases']) < self.cases_num:
                    self.sub_re_rules[rule]['cases'].add(re_obj.group())
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

    def _debug_rm_str_seg(self, text: str) -> None:
        '''
        Modify 'self.rm_str_seg' according to the matching times, the execute time, matching examples.
        '''
        for rule in self.debug_rm_str_seg:
            # self.rm_str_rules[rule] = {'match ratio': 0, 'avg time': 0, 'cases': []}
            tmp = text.find(rule)
            if tmp != -1:
                self.rm_str_seg[rule]['match ratio'] += 1
                if len(self.rm_str_seg[rule]['cases']) < self.cases_num:
                    self.rm_str_seg[rule]['cases'].add(text[tmp:])
            # start = time.time()
            self.rm_str_seg[rule]['avg time'] -= time.time()
            text = text[0: text.find(rule)]
            # end = time.time()
            self.rm_str_seg[rule]['avg time'] += time.time()
        
    def _pie_chart(self, data: dict, fig_path: str, title: str) -> None:
        if os.path.exists(fig_path): os.remove(fig_path)
        labels = data.keys()
        sizes = data.values()
        colors = cm.Set1(range(len(labels)))
        plt.clf()
        plt.cla()
        plt.figure(figsize=(6, 6)) 
        plt.pie(sizes, labels=labels, colors=colors, autopct='%.2f%%', startangle=90) 
        plt.legend()
        plt.axis('equal')
        plt.title(title, y=0.95, fontsize=16)
        plt.savefig(fig_path, transparent=True)

    def _histogram(self, data: list, fig_path: str, title: str) -> None:
        if os.path.exists(fig_path): os.remove(fig_path)
        plt.clf()
        plt.cla()
        bin_width = (max(data) - min(data)) / np.sqrt(len(data))
        num_bins = int(np.ceil((max(data) - min(data)) / bin_width))
        sns.displot(data, bins=num_bins)        
        plt.title(title, y=0.95, fontsize=16)
        # plt.xlabel('Value')
        # plt.ylabel('Frequency')
        plt.savefig(fig_path, transparent=True)


