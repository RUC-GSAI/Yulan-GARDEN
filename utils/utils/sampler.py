import json
import random
import os
import logging
import numpy as np
import matplotlib.pyplot as plt

from typing import TypedDict
from tqdm import tqdm

# from utils.utils.logger import Logger

textkey = 'Content'

class SampleConfig(TypedDict):
    input_path: str = ""
    output_path: str = ""
    if_sample_randomly: bool = True
    SAMPLE_RANDOMLY_NUM: int = 100
    if_sample_by_length: bool = False
    SAMPLE_BY_LENGTH_NUM: int = 50
    SAMPLE_BY_LENGTH_PROPORTION: int = 10

class Sampler():
    def __init__(self, sample_config: SampleConfig=None):
        self.input_path = ""
        self.output_path = ""
        self.output_to_file = True
        self.if_sample_randomly = True
        self.SAMPLE_RANDOMLY_NUM = 100
        self.SAMPLE_RANDOMLY_PROPORTION = 1.2
        self.if_sample_by_length = False
        self.SAMPLE_BY_LENGTH_NUM = 50
        self.SAMPLE_BY_LENGTH_PROPORTION = 10

        if sample_config is not None:
            self.input_path = sample_config.get("input_path", "")
            self.output_path = sample_config.get("output_path", "")
            self.output_to_file = sample_config.get("output_to_file", True)
            self.if_sample_randomly = sample_config.get("if_sample_randomly", True)
            self.SAMPLE_RANDOMLY_NUM = sample_config.get("SAMPLE_RANDOMLY_NUM", 100)
            self.if_sample_by_length = sample_config.get("if_sample_by_length", False)
            self.SAMPLE_BY_LENGTH_NUM = sample_config.get("SAMPLE_BY_LENGTH_NUM", 50)
            self.SAMPLE_BY_LENGTH_PROPORTION = sample_config.get("SAMPLE_BY_LENGTH_PROPORTION", 10)

        self.logger = logging.getLogger("Sampler_Logger")
        file_handler = logging.FileHandler("process.log")
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.INFO)
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        self.logger.info(f"current sampler configuration: \n {sample_config}")
    
    def _calculate_work_count(self, work) -> int:
        work_count = 0
        work_count += int(os.popen('wc -l %s' % work).read().split()[0])
        return work_count

    def sample_randomly(self) -> None:
        line_num = self._calculate_work_count(self.input_path)
        ret = []

        self.logger.info(f"begin to sample randomly {self.SAMPLE_RANDOMLY_NUM} / {line_num} lines from {self.input_path}..")
        
        with open(self.input_path, mode='r', encoding="utf-8") as fr, open(os.path.join(self.output_path, 'random.jsonl'), mode='w') as fw:
            cnt = 0
            for line in fr:
                if random.random() <= self.SAMPLE_RANDOMLY_NUM / line_num * self.SAMPLE_RANDOMLY_PROPORTION:
                    if self.output_to_file:
                        fw.write(line)
                    else:
                        ret.append(line)
                    cnt += 1
                if cnt >= self.SAMPLE_RANDOMLY_NUM:
                    break
        
        if self.output_to_file:
            self.logger.info(f"finish sample randomly {self.SAMPLE_RANDOMLY_NUM} / {line_num} lines into {os.path.join(self.output_path, 'random.jsonl')}..")
        else:
            self.logger.info(f"finish sample randomly {self.SAMPLE_RANDOMLY_NUM} / {line_num} lines..")
            return ret

    def gen_length_statistic(self, len_list: list):
        mean = np.mean(len_list)
        std_deviation = np.std(len_list)
        quartiles = np.percentile(len_list, [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]) 

        print("mean:", mean)
        print("std:", std_deviation)
        print("quartiles:", quartiles)

    def gen_length_histogram(self, len_list: list):
        import seaborn as sns
        sns.displot(len_list)

        # hist, bins = np.histogram(len_list, bins = 20)
        # plt.hist(len_list, bins=20)
        plt.savefig('./1.png')

    def calc_length_threshold(self):
        len_arr = []
        with open(self.input_path, mode='r', encoding='utf-8') as fr:
            for line in tqdm(fr, desc='calc_length_threshold'):
                ndata = json.loads(line)
                len_arr.append(len(ndata[textkey]))

        len_arr = sorted(len_arr, reverse=False)
        self.gen_length_statistic(len_arr)
        self.gen_length_histogram(len_arr)
        assert len(len_arr) >= self.SAMPLE_BY_LENGTH_NUM * self.SAMPLE_BY_LENGTH_PROPORTION * 2
        return len_arr[self.SAMPLE_BY_LENGTH_NUM * self.SAMPLE_BY_LENGTH_PROPORTION], len_arr[-self.SAMPLE_BY_LENGTH_NUM * self.SAMPLE_BY_LENGTH_PROPORTION]

    def sample_by_length(self) -> None:
        short_threshold, long_threshold = self.calc_length_threshold()
        # EXTREMELY SHORT
        line_num = self._calculate_work_count(self.input_path)
        self.logger.info(f"begin to sample short text {self.SAMPLE_BY_LENGTH_NUM} / {line_num} lines from {self.input_path}..")
        with open(self.input_path, mode='r', encoding="utf-8") as fr, open(os.path.join(self.output_path, 'short.jsonl'), mode='w') as fw:
            cnt = 0
            for line in fr:
                cur_len = len(json.loads(line)[textkey])
                if cur_len <= short_threshold:
                    if random.random() <= 1 / self.SAMPLE_BY_LENGTH_PROPORTION:
                        fw.write(line)
                        cnt += 1
                    if cnt >= self.SAMPLE_BY_LENGTH_NUM:
                        break
        self.logger.info(f"finish sample short text {self.SAMPLE_BY_LENGTH_NUM} / {line_num} lines into {os.path.join(self.output_path, 'short.jsonl')}..")

        # EXTREMELY LONG
        self.logger.info(f"begin to sample long text {self.SAMPLE_BY_LENGTH_NUM} / {line_num} lines from {self.input_path}..")
        with open(self.input_path, mode='r', encoding="utf-8") as fr, open(os.path.join(self.output_path, 'long.jsonl'), mode='w') as fw:
            cnt = 0
            for line in fr:
                cur_len = len(json.loads(line)[textkey])
                if cur_len >= long_threshold:
                    if random.random() <= 1 / self.SAMPLE_BY_LENGTH_PROPORTION:
                        fw.write(line)
                        cnt += 1
                    if cnt >= self.SAMPLE_BY_LENGTH_NUM:
                        break
        self.logger.info(f"finish sample long text {self.SAMPLE_BY_LENGTH_NUM} / {line_num} lines into {os.path.join(self.output_path, 'long.jsonl')}..")

    def do_sample(self):
        if self.if_sample_randomly:
            self.sample_randomly()
        if self.if_sample_by_length:
            self.sample_by_length()

if __name__ == '__main__':
    sampleconfig = SampleConfig()
    # sampleconfig["input_path"] = "/fs/archive/share/u2022101014/chinesewebtext/filtered/hot_20000_cleaned_v4.jsonl"
    # sampleconfig["input_path"] = "/fs/archive/share/u2022101014/baike_triple/10.jsonl"
    # sampleconfig["output_path"] = "/home/u2022101014/ZHEM/utils/test_files/texts/cleaned_old"
    sampleconfig["input_path"] = "/fs/archive/share/u2022101014/ZWJCYLK/ZWJCYLK-3/29.json"
    sampleconfig["output_path"] = "/fs/archive/share/u2022101014/ZWJCYLK/sampled"
    sampleconfig["SAMPLE_RANDOMLY_NUM"] = 500
    sampleconfig["if_sample_by_length"] = True
    sampleconfig["SAMPLE_BY_LENGTH_NUM"] = 250

    sampler = Sampler(sampleconfig)
    sampler.do_sample()