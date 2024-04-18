import json
import random
import os
import logging
import numpy as np
import matplotlib.pyplot as plt

from typing import TypedDict
from tqdm import tqdm

from utils.utils.logger import global_logger

textkey = 'text'

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
        self.if_sample = True
        self.input_path = ""
        self.output_path = ""
        self.output_to_file = True
        self.if_sample_randomly = True
        self.SAMPLE_RANDOMLY_NUM = 100
        self.SAMPLE_RANDOMLY_PROPORTION = 1.2
        self.if_sample_by_length = True
        self.SAMPLE_BY_LENGTH_NUM = 50
        self.SAMPLE_BY_LENGTH_PROPORTION = 10

        if sample_config is not None:
            self.if_sample = sample_config.get("if_sample", True)
            self.input_path = sample_config.get("input_path", "")
            self.output_path = sample_config.get("output_path", "")            
            self.output_to_file = sample_config.get("output_to_file", True)
            self.if_sample_randomly = sample_config.get("if_sample_randomly", True)
            self.SAMPLE_RANDOMLY_NUM = sample_config.get("SAMPLE_RANDOMLY_NUM", 100)
            self.if_sample_by_length = sample_config.get("if_sample_by_length", False)
            self.SAMPLE_BY_LENGTH_NUM = sample_config.get("SAMPLE_BY_LENGTH_NUM", 50)
            self.SAMPLE_BY_LENGTH_PROPORTION = sample_config.get("SAMPLE_BY_LENGTH_PROPORTION", 10)
    
    def _calculate_work_count(self, work) -> int:
        work_count = 0
        work_count += int(os.popen('wc -l %s' % work).read().split()[0])
        return work_count

    def _sample_randomly(self, input_path) -> None:
        line_num = self._calculate_work_count(input_path)
        ret = []
        
        global_logger.log_text(f"begin to sample randomly {self.SAMPLE_RANDOMLY_NUM} / {line_num} lines from {input_path}..")
        
        # mode: append (if self.input_path is a list, there may be many writings)
        with open(input_path, mode='r', encoding="utf-8") as fr, open(self.output_path, mode='a') as fw:
            cnt = 0
            for line in fr:
                if random.random() <= self.SAMPLE_RANDOMLY_NUM / line_num * self.SAMPLE_RANDOMLY_PROPORTION:
                    if self.output_to_file:
                        fw.write(line)
                    else:
                        ret.append(json.loads(line))
                    cnt += 1
                if cnt >= self.SAMPLE_RANDOMLY_NUM:
                    break
                
        if self.output_to_file:
            global_logger.log_text(f"finish sample randomly {self.SAMPLE_RANDOMLY_NUM} / {line_num} lines into {self.output_path}..")
            return None
        else:
            global_logger.log_text(f"finish sample randomly {self.SAMPLE_RANDOMLY_NUM} / {line_num} lines..")
            return ret
        
    def _no_sample(self, input_path) -> None:
        global_logger.log_text(f"begin to dump all lines from {input_path}..")
        
        # mode: append (if self.input_path is a list, there may be many writings)
        with open(input_path, mode='r', encoding="utf-8") as fr, open(self.output_path, mode='a') as fw:
            cnt = 0
            for line in fr:
                fw.write(line)
                cnt += 1
                
        global_logger.log_text(f"finish dump all lines into {self.output_path}..")
        
    def sample_randomly_works(self) -> None:
        '''
        self.input_path can be a work list (from prepare_works) or a file
        '''
        # to clear the file: self.output_path
        with open(self.output_path, mode='w') as fw:
            pass   
        if self.if_sample:             
            if isinstance(self.input_path, list):
                for input_path in self.input_path:
                    self._sample_randomly(input_path)
            else:
                self._sample_randomly(self.input_path)
        else:
            if isinstance(self.input_path, list):
                for input_path in self.input_path:
                    print(input_path)
                    self._no_sample(input_path)
            else:
                self._no_sample(self.input_path)

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
        global_logger.log_text(f"begin to sample short text {self.SAMPLE_BY_LENGTH_NUM} / {line_num} lines from {self.input_path}..")
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
        global_logger.log_text(f"finish sample short text {self.SAMPLE_BY_LENGTH_NUM} / {line_num} lines into {os.path.join(self.output_path, 'short.jsonl')}..")

        # EXTREMELY LONG
        global_logger.log_text(f"begin to sample long text {self.SAMPLE_BY_LENGTH_NUM} / {line_num} lines from {self.input_path}..")
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
        global_logger.log_text(f"finish sample long text {self.SAMPLE_BY_LENGTH_NUM} / {line_num} lines into {os.path.join(self.output_path, 'long.jsonl')}..")

    def do_sample(self):
        if self.if_sample_randomly:
            self.sample_randomly_works()
        if self.if_sample_by_length:
            self.sample_by_length()

if __name__ == '__main__':
    # sampleconfig = SampleConfig()
    # # sampleconfig["input_path"] = "/fs/archive/share/u2022101014/chinesewebtext/filtered/hot_20000_cleaned_v4.jsonl"
    # # sampleconfig["input_path"] = "/fs/archive/share/u2022101014/baike_triple/10.jsonl"
    # # sampleconfig["output_path"] = "/home/u2022101014/ZHEM/utils/test_files/texts/cleaned_old"
    # sampleconfig["input_path"] = "/fs/archive/share/u2022101014/ZWJCYLK/ZWJCYLK-3/29.json"
    # sampleconfig["output_path"] = "/fs/archive/share/u2022101014/ZWJCYLK/sampled"
    # sampleconfig["SAMPLE_RANDOMLY_NUM"] = 500
    # sampleconfig["if_sample_by_length"] = True
    # sampleconfig["SAMPLE_BY_LENGTH_NUM"] = 250

    # sampler = Sampler(sampleconfig)
    # sampler.sample_randomly_works()

    # config = {'input_path': ["/home/u2022101014/ZHEM/bash/random_filtered.jsonl", "/home/u2022101014/ZHEM/bash/random_filtered_1.jsonl"],
    #           'output_path': "/fs/archive/share/u2022101014/CICG_zh/data_sampled/cleaned_1/raw.jsonl",
    #           'if_sample_randomly': True,
    #           'SAMPLE_RANDOMLY_NUM': 10}
    # sampler = Sampler(SampleConfig(config))
    # # print(sampler.input_path)
    # sampler.sample_randomly_works()

    # import matplotlib.pyplot as plt
    # from matplotlib import cm

    # import os

    # file_path = "/fs/archive/share/u2022101014/data/openwebtext2/sample/raw.jsonl"
    # output_path = "/fs/archive/share/u2022101014/data/openwebtext2/sample/raw_new.jsonl"
    # # file_path = "/fs/archive/share/u2022101014/data/openwebtext2/clean_v2/raw.jsonl"
    # # output_path = "/home/u2022101014/ZHEM/bash/owt_1w.jsonl"
    # target_size = 1024 * 1024 * 1024  # 1GB
    # # target_size = 1024 * 1024

    # total_size = 0
    # num_lines = 0
    # lines = []

    # with open(file_path, "r") as file, open(output_path, "w") as fw:
    #     while total_size <= target_size:
    #         line = file.readline()
    #         if not line:
    #             break

    #         # lines.append(line)
            
    #         total_size += len(line.encode())

    #         if total_size > target_size:
    #             break

    #         fw.write(line)
    #         num_lines += 1

    # # 打印读取的行数和累计数据大小
    # # print("读取的行数:", len(lines))
    # print("累计数据大小:", total_size)
    # print(num_lines)

    # # 处理读取到的行数据
    # # ...
    import re
    dic = {"text": "Libya ( ; , ), officially the State of Libya , is a country in the Maghreb region of North Africa. It is bordered by the Mediterranean Sea to the north, Egypt to the east, Sudan to the southeast, Chad to the south, Niger to the southwest, Algeria to the west, and Tunisia to the northwest. Libya comprises three historical regions: Tripolitania,"}
    text = dic['text']
    # pattern = r
    # "## See also\n"
    # pattern = "#* See also\n"
    
    with open('/home/u2022101014/ZHEM/utils/utils/input_path.json', 'r') as fr:
        input_path = json.load(fr)
    for a in input_path:
        print(a.split('/')[-1])
