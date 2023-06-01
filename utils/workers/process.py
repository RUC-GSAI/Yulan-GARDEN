from utils.settings import *
from utils.parallel import *
from utils.rules import *
from dumper import *

import os

def prepare_works(input_path: str, input_ext: str='') -> list:
    works = []
    for root, dirs, files in os.walk(input_path):
        for each in files:
            if each.endswith(input_ext):
                works.append(os.path.join(root, each))
    return works    

def process_work(conf: Settings):
    settings = conf.settings
    input_path, input_ext, output_path = settings['input_path'], settings['input_ext'], settings['output_path']

    if settings['if_filter'] or settings['if_clean']:
        # specify work path
        if settings['if_parallel']:
            parallel_paras = settings['parallel_paras']
            # todo: chunk_size
            prepare_parallel_works(input_path=input_path, output_path=output_path, input_ext='?', source_tag='?', n_process= parallel_paras['n_process'])
            work_path = os.path.join(output_path, '.tmp')
        else:
            work_path = os.path.join(output_path, '.tmp')
            if input_ext in TXT_SUFFIX:
                dump_txts2jsonl(input_path=input_path, output_path=work_path, source_tag='?')
                work_path = os.path.join(output_path, '.tmp')
            elif input_ext in JSONL_SUFFIX:
                dump_jsonls2jsonl(input_path=input_path, output_path=work_path, source_tag='?')
                work_path = input_path
    if settings['if_merge']:
        # todo
        pass

    if settings['if_cut']:
        # todo
        pass