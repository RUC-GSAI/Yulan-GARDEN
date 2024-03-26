from utils.cleaner import *
from utils.settings import *
from utils.utils.my_funcs import *

class Cleaner():
    def __init__(self, setting: Settings=None) -> None:
        self.clean_setting = {}
        
        if setting:
            self.load_settings(setting=setting)
            self.cleaner_ops = {
                "CleanerRemoveLineByRegExp": CleanerRemoveLineByRegExp(),
                "CleanerRemoveLineByText": CleanerRemoveLineByText(),
                "CleanerRemovePassageInvisbleChars": CleanerRemovePassageInvisbleChars(),
                "CleanerRemovePassageNewline": CleanerRemovePassageNewline(),
                "CleanerRemovePassageRegExp": CleanerRemovePassageRegExp(),
                "CleanerRemoveSegmentByText": CleanerRemoveSegmentByText(),
                "CleanerRemoveSegmentByRegExp": CleanerRemoveSegmentByRegExp(),
                "CleanerRemovePassageText": CleanerRemovePassageText(),
                "CleanerSubstitutePassageRegExp": CleanerSubstitutePassageRegExp(),
                "CleanerSubstitutePassageBySelfDefinedFunctions": CleanerSubstitutePassageBySelfDefinedFunctions(),
                "CleanerSubstitutePassageSimplifiedChinese": CleanerSubstitutePassageSimplifiedChinese(),
                "CleanerSubstitutePassageEmail": CleanerSubstitutePassageEmail(),
                "CleanerSubstitutePassageIDCard": CleanerSubstitutePassageIDCard(),
                "CleanerSubstitutePassageIP": CleanerSubstitutePassageIP(),
                "CleanerSubstitutePassagePhone": CleanerSubstitutePassagePhone(),
                "CleanerSubstitutePassageURL": CleanerSubstitutePassageURL(),
                "CleanerDedupLineByNgram": CleanerDedupLineByNgram(),
            }

    def load_settings(self, setting: Settings) -> None:
        self.if_clean = setting.get('if_clean', False)
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
        self.rm_re_seg = self.clean_setting['rm_re_seg']['re_list'] if self.clean_setting['rm_re_seg']['use'] else []
        self.tra2sim = self.clean_setting['tra2sim']
        self.rm_email = self.clean_setting['rm_pii']['details']['email'] if self.clean_setting['rm_pii']['use'] else False
        self.rm_idcard = self.clean_setting['rm_pii']['details']['idcard'] if self.clean_setting['rm_pii']['use'] else False
        self.rm_ip = self.clean_setting['rm_pii']['details']['ip'] if self.clean_setting['rm_pii']['use'] else False
        self.rm_phone = self.clean_setting['rm_pii']['details']['phone'] if self.clean_setting['rm_pii']['use'] else False
        self.rm_url = self.clean_setting['rm_pii']['details']['url'] if self.clean_setting['rm_pii']['use'] else False
        self.dedup_line_ngram = self.clean_setting['dedup_line_ngram']
        self.dedup_line_n, self.dedup_line_thresim = self.dedup_line_ngram["n"], self.dedup_line_ngram["thre_sim"]

    def clean_single_text(self, text: str) -> str:
        # if self.if_clean == False, then do not clean, just return origin text {{text}}
        if not self.if_clean:
            return text
        
        if self.my_funcs['use']:
            text = self.cleaner_ops['CleanerSubstitutePassageBySelfDefinedFunctions'].clean_single_text(text, self.my_funcs['funcs'])
        if self.rm_crawlerchars['use']:
            text = self.cleaner_ops['CleanerRemovePassageInvisbleChars'].clean_single_text(text)
        if self.sub_newline['use']:
            text = self.cleaner_ops['CleanerRemovePassageNewline'].clean_single_text(text)
        if len(self.rm_re_rules) > 0:
            for rm_re in self.rm_re_rules:
                text = self.cleaner_ops['CleanerRemovePassageRegExp'].clean_single_text(text, rm_re)
        if len(self.sub_re_rules) > 0:
            for sub_re, repl_text in self.sub_re_rules.items():
                text = self.cleaner_ops['CleanerSubstitutePassageRegExp'].clean_single_text(text, sub_re, repl_text)
        if len(self.rm_str_rules) > 0:
            for rm_str in self.rm_str_rules:
                text = self.cleaner_ops['CleanerRemovePassageText'].clean_single_text(text, rm_str)
        if len(self.rm_str_seg) > 0:
            for rm_str in self.rm_str_seg:
                text = self.cleaner_ops['CleanerRemoveSegmentByText'].clean_single_text(text, rm_str)
        if len(self.rm_re_seg) > 0:
            for rm_re in self.rm_re_seg:
                text = self.cleaner_ops['CleanerRemoveSegmentByRegExp'].clean_single_text(text, rm_re)
        if len(self.rm_str_lines) > 0:
            text = self.cleaner_ops['CleanerRemoveLineByText'].clean_single_text(text, self.rm_str_lines)
        if len(self.rm_re_lines) > 0:
            text = self.cleaner_ops['CleanerRemoveLineByRegExp'].clean_single_text(text, self.rm_re_lines)
        if self.tra2sim['use']:
            target = self.tra2sim['target']
            text = self.cleaner_ops['CleanerSubstitutePassageSimplifiedChinese'].clean_single_text(text, target)
        if self.sub_newline['use']:
            text = self.cleaner_ops['CleanerRemovePassageNewline'].clean_single_text(text)
        if self.rm_email:
            text = self.cleaner_ops['CleanerSubstitutePassageEmail'].clean_single_text(text)
        if self.rm_idcard:
            text = self.cleaner_ops['CleanerSubstitutePassageIDCard'].clean_single_text(text)
        if self.rm_ip:
            text = self.cleaner_ops['CleanerSubstitutePassageIP'].clean_single_text(text)
        if self.rm_phone:
            text = self.cleaner_ops['CleanerSubstitutePassagePhone'].clean_single_text(text)
        if self.rm_url:
            text = self.cleaner_ops['CleanerSubstitutePassageURL'].clean_single_text(text)
        if self.dedup_line_ngram['use']:
            text = self.cleaner_ops['CleanerDedupLineByNgram'].clean_single_text(text, self.dedup_line_n, self.dedup_line_thresim)
        return text