import json
import os

from multiprocessing import cpu_count, Pool
from tqdm import tqdm

from utils.settings import *

from utils.workers import *
from utils.utils import prepare_works, modulemanager

def _now_timestamp():
    from datetime import datetime
    return int(datetime.now().timestamp())

def _split_into_chunks(works: list, pieces: int) -> list:
    pieces = max(1, pieces)
    return [works[i: i + pieces] for i in range(0, len(works), pieces)]

def _process_single_text(text: str) -> str:
    '''
    Return "" (an empty string) means the text is Filtered.
    Else return an extracted and cleaned module
    '''
    extract_module = modulemanager.extract_module
    clean_module = modulemanager.clean_module
    filter_module = modulemanager.filter_module

    text = extract_module.extract(text)
    if filter_module.filter_single_text(text):
        return ""
    text = clean_module.clean_single_text(text)
    if filter_module.filter_single_text(text):
        return ""    
    return text

def _process_single_work(work_path: str, output_path: str, text_key: str="text") -> int:
    '''
    Return tot_cnt, succ_cnt if the process runs successfully.
    '''
    # prepare name of input file and output file
    tot_cnt, succ_cnt, ifile_path = 0, 0, work_path
    idir_name, ifname = os.path.split(work_path)
    if not os.path.exists(output_path): os.makedirs(output_path, exist_ok=True)
    fname, fext = os.path.splitext(ifname)
    ofile_path = os.path.join(output_path, f'{_now_timestamp()}-{fname}.{fext}')

    # do single work
    with open(ifile_path, mode='r', encoding='utf-8') as fr, open(ofile_path, mode='w', encoding='utf-8') as fw:
        for line in fr:
            try:
                tot_cnt += 1
                nrecord = json.loads(line)
                text = _process_single_text(nrecord[text_key])
                if text != "":
                    nrecord[text_key] = text
                    fw.write(json.dumps(nrecord, ensure_ascii=False) + '\n')
                succ_cnt += 1
            except Exception as ne:
                # continue
                print(f'Exception for Bad File at {ifile_path} for {ne}\n')
    return (tot_cnt, succ_cnt)

def process_parallel_works(work_path: str, output_path: str, parallel_paras, text_key: str):
    # Prepare parameters
    n_process = cpu_count() - 1 if parallel_paras['n_process'] <= 1 else parallel_paras['n_process'] - 1
    chunk_size = n_process * 3 if parallel_paras['chunk_size'] <= 0 else parallel_paras['chunk_size']
    pool = Pool(n_process)
    assert(n_process > 0 and chunk_size > 0)

    # Prepare works
    worklist = prepare_works(work_path, input_ext='jsonl')
    work_chunks = _split_into_chunks(worklist, chunk_size)

    # Do works parallelly with multiprocessing
    pbar = tqdm(work_chunks, total=len(work_chunks), desc="Processing works parallelly")
    tot_cnt, succ_cnt = 0, 0
    for count, chunk in enumerate(pbar):
        '''
        Each single process deal with its work in Function @process_single_work
        Params:
            @  zip(<params pass to function @process_single_work>) packed as a zip
        '''
        works_out = pool.starmap(_process_single_work, 
                                 zip(chunk, [output_path] * len(chunk), [text_key] * len(chunk)))
        for each in works_out:
            tot_cnt, succ_cnt = tot_cnt + each[0], succ_cnt + each[1]
        success_rate = succ_cnt / tot_cnt
        pbar.set_postfix({"Success Rate": success_rate})
    return success_rate