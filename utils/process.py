from utils.settings import *
from utils.parallel import prepare_parallel_works, process_parallel_works
from utils.rules import *
from utils.dumper import *
from utils.cleaner import *
from utils.filter import *
from utils.extractor import *

from tqdm import tqdm

from utils.utils import prepare_works
from utils.debugger import log_text

import os   

def process_work_mult_threads(work_path: str, output_path: str, extract_module: Extractor, clean_module: Cleaner, filter_module: Filter, parallel_paras, text_key: str):
    process_parallel_works(work_path, output_path, extract_module, clean_module, filter_module, parallel_paras, text_key)

def process_work_single_thread(work_path: str, output_path: str, extract_module: Extractor, clean_module: Cleaner, filter_module: Filter):
    if not os.path.exists(output_path): os.makedirs(output_path, exist_ok=True)
    for file in tqdm(prepare_works(work_path), desc='Process work single thread'):
        filename = os.path.basename(file)
        nwork_in = os.path.join(work_path, file)
        nwork_out = os.path.join(output_path, filename)
        log_text(f"work_in_path: {nwork_in}, work_out_path: {nwork_out}")
        assert(nwork_in != nwork_out)
        try:
            with open(nwork_in, mode='r', encoding='utf-8') as fr, open(nwork_out, mode='w', encoding='utf-8') as fw:
                for line in fr:
                    nrecord = json.loads(line)
                    text = process_single_text(nrecord['content'], extract_module, clean_module, filter_module)
                    if text != "":
                        nrecord['text'] = text
                        fw.write(json.dumps(nrecord, ensure_ascii=False) + '\n')
        except Exception as ne:
            print(f"Bad work {nwork_in} for Exception {ne}")

def process_single_text(text: str, extract_module: Extractor, clean_module: Cleaner, filter_module: Filter) -> str:
    '''
    Return "" (an empty string) means the text is Filtered.
    Else return an extracted and cleaned module
    '''
    text = extract_module.extract(text)
    if filter_module.filter_single_text(text):
        return ""
    text = clean_module.clean_single_text(text)
    if filter_module.filter_single_text(text):
        return ""    
    return text

def process_work(conf: Settings):
    settings = conf.settings
    input_path, input_ext, output_path = settings['input_path'], settings['input_ext'], settings['output_path']

    if settings['if_filter'] or settings['if_clean']:
        if settings['if_parallel']:
            parallel_paras = settings['parallel_paras']
            # todo: chunk_size
            prepare_parallel_works(input_path=input_path, output_path=output_path, input_ext=input_ext, source_tag='?', n_process= parallel_paras['n_process'])
            work_path = os.path.join(output_path, '.tmp')
        else:
            work_path = os.path.join(output_path, '.tmp')
            if input_ext in TXT_SUFFIX:
                dump_txts2jsonl(
                    input_path=input_path, 
                    output_path=work_path, 
                    keep_text_only=False,
                    source_tag='?'
                )
            elif input_ext in JSONL_SUFFIX:
                dump_jsonls2jsonl(
                    input_path=input_path, 
                    output_path=work_path, 
                    keep_text_only=False,
                    source_tag='?'
                )
        
        # load settings for modules
        extract_module = Extractor(setting=settings)
        clean_module = Cleaner(setting=settings)
        filter_module = Filter(setting=settings)

        # do work and calculate work statistics
        log_text(f"Parallel Setting: {settings['if_parallel']}")
        if settings['if_parallel']:
            process_work_mult_threads(
                # todo: text_key
                work_path=work_path, 
                output_path=os.path.join(output_path, '.cleaned'), 
                extract_module=extract_module, 
                clean_module=clean_module, 
                filter_module=filter_module, 
                parallel_paras=parallel_paras,
                text_key="content")
            dump_jsonls2jsonl(
                input_path=os.path.join(output_path, '.cleaned'),
                output_path=os.path.join(output_path, 'out'),
                keep_text_only=True
            )
            log_text(f"Final data dir: {os.path.join(output_path, 'out')}")
        else:
            process_work_single_thread(
                work_path=work_path, 
                output_path=os.path.join(output_path, '.cleaned'), 
                extract_module=extract_module, 
                clean_module=clean_module, 
                filter_module=filter_module)
            dump_jsonls2jsonl(
                input_path=os.path.join(output_path, '.cleaned'),
                output_path=os.path.join(output_path, 'out'),
                keep_text_only=True
            )
            log_text(f"Final data dir: {os.path.join(output_path, 'out')}")

    if settings['if_merge']:
        # todo
        pass

    if settings['if_cut']:
        # todo
        pass