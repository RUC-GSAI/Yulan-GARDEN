from utils.settings import *
import json
import os
import datasets

class Deduplicator:
    def __init__(self, setting: Settings=None) -> None:
        self.dedup_setting = {}
        self.load_settings(setting=setting)
    
    def load_settings(self, setting: Settings) -> None:
        self.dedup_setting = setting['dedup_paras']

        self.input_file = os.path.join(setting['output_path'], 'out/tmp.jsonl')
        self.tmp_file = os.path.join(setting['output_path'], 'out/tmp.json')
        self.tmp_dir = os.path.join(setting['output_path'], '.dedup')
        self.output_file = os.path.join(setting['output_path'], 'out/dedup.jsonl')
        self.language = self.dedup_setting['language']
        self.column = setting['input_text_key']
        self.ngram = self.dedup_setting['ngram']
        self.num_perm = self.dedup_setting['num_perm']
        self.min_length = self.dedup_setting['min_length']
        self.threshold = self.dedup_setting['threshold']

    def transform_jsonl_to_json(self):
        dataset = []
        with open(self.tmp_file, "w", encoding="utf-8") as fw:
            with open(self.input_file, "r", encoding="utf-8") as fr:
                for idx, line in enumerate(fr):
                    if idx % 1000000 == 0:
                        print(idx)
                    line = line.strip()
                    data = json.loads(line)
                    dataset.append(data)
            jsondata = json.dumps(dataset, indent=4, ensure_ascii=False)
            fw.write(jsondata)
        del jsondata

    def transform_json_to_json(self):
        dataset = []
        with open(self.tmp_file, "w", encoding="utf-8") as fw:
            with open(self.input_file, "r", encoding="utf-8") as fr:
                dataset = json.load(fr)
            jsondata = json.dumps(dataset, indent=4, ensure_ascii=False)
            fw.write(jsondata)
        del jsondata

    def transformer_dedup_data_into_jsonl(self):
        d = datasets.load_from_disk(self.tmp_dir)
        with open(self.output_file, "w", encoding="utf-8") as fw:
            for i, data in enumerate(d):
                # if i % 500000 == 0:
                # print(i)
                fw.write(json.dumps(data, ensure_ascii=False) + "\n")
                fw.flush()

    def dedup(self):
        # print("=====> Transform jsonl file to json file " + self.tmp_file)
        self.transform_jsonl_to_json()
        # print("=====> Dedupicate data " + self.tmp_dir)
        if not os.path.exists(self.tmp_dir):
            os.makedirs(self.tmp_dir)        
        dedup_command_line = "cd utils/text-dedup; python3 -m text_dedup.minhash --data_files {0} --split train --path json --cache_dir ~/.cache/ --output {1} --column {2} --batch_size 50000 --num_perm {3} --ngram {4} --min_length {5} --threshold {6}".format(self.tmp_file, self.tmp_dir, self.column, self.num_perm, self.ngram, self.min_length, self.threshold)
        os.system(dedup_command_line)
        # print("=====> Convert to jsonl file " + self.output_file)
        self.transformer_dedup_data_into_jsonl()
        # print("=====> finish all!!!")