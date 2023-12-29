from utils.filter.filter_base import FilterBase
from utils.evaluator import LangIdentifier, PerplexityEvaluator
from utils.utils.sampler import SampleConfig, Sampler

from collections import defaultdict
from utils.utils.logger import global_logger

import numpy as np

class FilterPassageByPPL(FilterBase):
    '''
    The Subclass of FilterBase class.
    '''
    def __init__(self, input_path: str = "") -> None:
        self.perplexity_evaluator = PerplexityEvaluator(
            model_path="/fs/archive/share/u2022101014/models/kenlm/"
        )
        self.sample_cnt = 0

        self.samplerconfig = SampleConfig()
        self.samplerconfig['input_path'] = input_path
        self.samplerconfig['output_to_file'] = False
        self.samplerconfig['if_sample_randomly'] = True
        self.samplerconfig['if_sample_by_length'] = False
        self.sampler = Sampler(
            self.samplerconfig
        )

        self.text_field = "text"
        self.lang_field = "language"
        self.langidentifier = LangIdentifier(
            model_path="/fs/archive/share/u2022101014/models/fasttext/lid.176.bin"
        )

        self.ppl_distributed = defaultdict(list)
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

        self._calc_filter_threshold()

        self.reject_cnt = 0
        self.accept_cnt = 0

    def _calc_filter_threshold(self) -> None:
        global_logger.log_text("Begin to Calculate the upper and lower bounds of the ppl filtering threshold..")

        # sampled items
        sampled_dt = self.sampler.sample_randomly()

        # label language of each item
        if self.lang_field in sampled_dt[0].keys():
            for dt in sampled_dt:
                dt["meta"][self.lang_field] = dt[self.lang_field]
        elif "meta" in sampled_dt[0].keys() and self.lang_field in sampled_dt[0]["meta"].keys():
            pass
        else:
            for dt in sampled_dt:
                dt["meta"][self.lang_field] = self.langidentifier.evaluate_single_text(dt)
        
        # calculate ppl of each sampled item
        for dt in sampled_dt:
            lang = dt["meta"][self.lang_field]
            ppl = self.perplexity_evaluator.evaluate_single_text(
                text = dt[self.text_field],
                lang = lang
            )
            self.ppl_distributed[lang].append(ppl)
        
        # determine the lower_bound and upper_bound according to the sampled items
        for lang in self.ppl_distributed:
            ndt = self.ppl_distributed[lang]
            mean, std_dev = np.mean(ndt), np.std(ndt)
            range_3sigma = [mean - (3 * std_dev), mean + (3 * std_dev)]
            self.ppl_filter_thresholds[lang]["lower_bound"] = range_3sigma[0]
            self.ppl_filter_thresholds[lang]["upper_bound"] = range_3sigma[1]
            global_logger.log_text(f"Calculating the upper({self.ppl_filter_thresholds[lang]['upper_bound']}) and lower({self.ppl_filter_thresholds[lang]['lower_bound']}) bounds of the ppl filtering threshold completed!!")

    def filter_single_text(self, text: str, lang: str = "") -> bool:      
        # label the language of current text
        if not lang:
            lang, score = self.langidentifier.evaluate_single_text(text)
        
        ppl = self.perplexity_evaluator.evaluate_single_text(
            text = text, 
            lang = lang
        )

        if ppl >= self.ppl_filter_thresholds[lang]["upper_bound"]:
            self.reject_cnt += 1
            return True
        else:
            self.accept_cnt += 1
            return False