from utils.filter.filter_base import FilterBase
from utils.evaluator import LangIdentifier, PerplexityEvaluator
from utils.utils.sampler import SampleConfig, Sampler

from collections import defaultdict
from utils.utils.logger import global_logger

import numpy as np
import os
import json

class FilterPassageByPPL(FilterBase):
    '''
    The Subclass of FilterBase class.
    '''
    def __init__(self, input_path: str = "", output_path: str = "", bound_path: str = "", sigma: float = 1.0) -> None:
        self.perplexity_evaluator = PerplexityEvaluator(
            model_path="utils/models/kenlm/"
        )
        self.sample_cnt = 0

        self.input_path, self.output_path, self.bound_path = input_path, output_path, bound_path
        self.sigma = sigma

        self.samplerconfig = SampleConfig()
        self.samplerconfig['input_path'] = input_path
        self.samplerconfig['output_path'] = output_path
        self.samplerconfig['SAMPLE_RANDOMLY_NUM'] = 500

        self.samplerconfig['output_to_file'] = False
        self.samplerconfig['if_sample_randomly'] = True
        self.samplerconfig['if_sample_by_length'] = False
        self.sampler = Sampler(
            self.samplerconfig
        )

        self.text_field = "text"
        self.lang_field = "language"
        self.langidentifier = LangIdentifier(
            model_path="utils/models/fasttext/lid.176.bin"
        )

        self.ppl_distributed = defaultdict(list)
        # for simplify code of this moduld, we move the process of calculating the filter threshold into utils/workers/debugger.py
        if os.path.exists(bound_path):
            with open(bound_path, "r") as fr:
                self.ppl_filter_thresholds = json.load(fr)
        else:
            self.ppl_filter_thresholds = None
        self.reject_cnt = 0
        self.accept_cnt = 0


    def calc_filter_threshold_without_debugger(self):
        dts = self.sampler._sample_randomly(self.input_path)
        ppls = defaultdict(list)
        for dt in dts:
            text = dt['text']
            lang_label, lang_score = self.langidentifier.evaluate_single_text(text)
            cur_ppl = self.perplexity_evaluator.evaluate_single_text(text, lang=lang_label[0])
            if cur_ppl is not None:
                ppls[lang_label[0]].append(cur_ppl)
        self.calc_filter_threshold(ppls=ppls, param=self.sigma)

    def calc_filter_threshold(self, ppls: dict, param: float) -> None:
        assert param > 0
        if self.ppl_filter_thresholds == None:
            self.ppl_filter_thresholds = {
                "en":{
                    "lower_bound": 0.0,
                    "upper_bound": 0.0 
                },
                "zh":{
                    "lower_bound": 0.0,
                    "upper_bound": 0.0
                },
                "uk":{
                    "lower_bound": 0.0,
                    "upper_bound": 0.0
                }
            }
        global_logger.log_text("Begin to Calculate the upper and lower bounds of the ppl filtering threshold..")
        self.ppl_distributed = ppls
        # determine the lower_bound and upper_bound according to the sampled items
        for lang in self.ppl_distributed:
            ndt = self.ppl_distributed[lang]
            mean, std_dev = np.mean(ndt), np.std(ndt)
            range_sigma = [mean - (param * std_dev), mean + (param * std_dev)]
            # range_3sigma = [mean - (2 * std_dev), mean + (2 * std_dev)]
            # range_3sigma = [mean - (std_dev), mean + (std_dev)]
            self.ppl_filter_thresholds[lang]["lower_bound"] = range_sigma[0]
            self.ppl_filter_thresholds[lang]["upper_bound"] = range_sigma[1]
            global_logger.log_text(f"For {lang}, calculating the upper bound({self.ppl_filter_thresholds[lang]['upper_bound']}) ({param} * sigma) of the ppl filtering threshold completed!!")

    def filter_single_text(self, text: str, lang: str="") -> bool:
        if self.ppl_filter_thresholds == None:
            self.calc_filter_threshold_without_debugger()
        # label the language of current text
        if len(lang) == 0:
            lang, scores = self.langidentifier.evaluate_single_text(text)
        lang = lang[0]
        ppl = self.perplexity_evaluator.evaluate_single_text(
            text = text, 
            lang = lang
        )
        # if we don't have language ppl model, ppl is None
        if ppl:
            if ppl >= self.ppl_filter_thresholds[lang]["upper_bound"]:
                self.reject_cnt += 1
                return True
            else:
                self.accept_cnt += 1
                return False
        return False