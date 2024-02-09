from utils.settings import *
from utils.parallel import prepare_parallel_works, process_parallel_works
from utils.rules import *
from utils.workers import *

from tqdm import tqdm

from utils.utils import *

import os   

from ast import literal_eval

def process_work_mult_threads(work_path: str, output_path: str, parallel_paras, text_key: str):
    process_parallel_works(work_path, output_path, parallel_paras, text_key)

def process_work_single_thread(work_path: str, output_path: str, text_key: str="text", input_ext: str='jsonl'):
    if not os.path.exists(output_path): os.makedirs(output_path, exist_ok=True)
    for file in tqdm(prepare_works(work_path, input_ext=input_ext), desc='Process work single thread'):
        filename = os.path.basename(file)
        nwork_in = os.path.join(work_path, file)
        nwork_out = os.path.join(output_path, filename)
        
        global_logger.log_text(f"work_in_path: {nwork_in}, work_out_path: {nwork_out}")
        print(f'{nwork_in} and {nwork_out}\n')
        assert(nwork_in != nwork_out)
        # try:
        with open(nwork_in, mode='r', encoding='utf-8') as fr, open(nwork_out, mode='w', encoding='utf-8') as fw:
            for line in fr:
                nrecord = json.loads(line)
                text, label = process_single_text(nrecord[text_key])
                # when label is False (no filter), the text is writen in nrecord whether the text is null
                if label == False:
                    nrecord[text_key] = text
                    fw.write(json.dumps(nrecord, ensure_ascii=False) + '\n')
        # except Exception as ne:
            # print(f"Bad work {nwork_in} for Exception {ne}")

def process_single_text(text: str) -> [str, bool]:
    '''
    Return "" (an empty string) means the text is Filtered.
    Else return an extracted and cleaned module
    '''
    extract_module = modulemanager.extract_module
    clean_module = modulemanager.clean_module
    filter_module = modulemanager.filter_module

    text = extract_module.extract(text)
    if filter_module.filter_single_text(text):
        return "", True
    text = clean_module.clean_single_text(text)
    if filter_module.filter_single_text(text):
        return "", True
    return text, False

def prepare_jsonl_files(settings: dict):
    '''
    step 1: prepare jsonl files
    '''
    input_path, input_ext, input_text_key, output_path, output_source_value = settings['input_path'], settings['input_ext'], settings['input_text_key'], settings['output_path'], settings['output_source_value']

    if settings['if_debug'] or settings['if_filter'] or settings['if_clean'] or settings['if_dedup']:
        # regularize extension of input file 
        if settings['if_parallel']:
            parallel_paras = settings['parallel_paras']
            # todo: chunk_size
            work_path = os.path.join(output_path, '.tmp')
            prepare_parallel_works(
                input_path=input_path, 
                output_path=work_path, 
                input_ext=input_ext, 
                source_tag=output_source_value,
                n_process=parallel_paras['n_process'],
                text_key=input_text_key
            )
        else:
            work_path = os.path.join(output_path, '.tmp')
            reformat_everything2jsonl(
                input_ext=input_ext,
                input_path=input_path,
                output_path=work_path,
                output_source_value=output_source_value
            )

def sample_debug(settings: dict, option: str):
    '''
    step 2 and 4: sample texts from raw/refined data, analyse by debugger
    '''
    assert option in ['raw', 'refined']
    input_path, input_ext, input_text_key, output_path, output_source_value = settings['input_path'], settings['input_ext'], settings['input_text_key'], settings['output_path'], settings['output_source_value']
    IF_SAMPLE = settings['debug_paras']['if_sample']
    
    debugger_module = Debugger(settings, option)
    if option == 'raw':
        work_path = os.path.join(output_path, '.tmp')
    else:
        work_path = os.path.join(output_path, 'out/dedup.jsonl') if settings['if_dedup'] else os.path.join(output_path, 'out/tmp.jsonl') 

    # generate debugger report
    debugger_worklist = prepare_works(work_path, input_ext='jsonl')
    # sample 'debug_sample_num_per_file' lines of each file in debugger_worklist
    sampler_config = {'input_path': debugger_worklist,
        'output_path': os.path.join(settings['output_path'], f'{option}.jsonl'),
        'if_sample': IF_SAMPLE,
        'if_sample_randomly': True,
        'SAMPLE_RANDOMLY_NUM': settings['debug_paras']['debug_sample_num_per_file']}
    sampler = Sampler(SampleConfig(sampler_config))
    sampler.sample_randomly_works()     
    debug_path = os.path.join(settings['output_path'], f'{option}.jsonl')

    with open(debug_path, mode='r', encoding='utf-8') as fr:
        cnt = 0
        for line in fr:
            cnt += 1
            text = json.loads(line)[input_text_key]
            # text = literal_eval(line)[input_text_key]
            debugger_module.debug_single_text(text)
    ppls = debugger_module.debug_params_report()
    with open(f'tmp/ppl_{option}.json', 'w') as fw:
        json.dump(ppls, fw, indent=4)
    global_logger.log_text(f"for {option} data: generating debug report {debugger_module.debug_report_path} finish..")
    if ppls:
        modulemanager.filter_module.filter_ops['FilterPassageByPPL'].calc_filter_threshold(ppls, settings['filter_paras']['fil_ppl']['param'])

def refining_process(settings: dict):
    '''
    step 3: refined data: cleaner, filter, deduplicator
    '''
    input_path, input_ext, input_text_key, output_path, output_source_value = settings['input_path'], settings['input_ext'], settings['input_text_key'], settings['output_path'], settings['output_source_value']
    work_path = os.path.join(output_path, '.tmp')

    if settings['if_filter'] or settings['if_clean']:
        # do work and calculate work statistics
        global_logger.log_text(f"Parallel Setting: {settings['if_parallel']}")
        if settings['if_parallel']:
            parallel_paras = settings['parallel_paras']
            process_work_mult_threads(
                work_path=work_path, 
                output_path=os.path.join(output_path, '.cleaned'), 
                parallel_paras=parallel_paras,
                text_key=input_text_key,
            )
            dump_jsonls2jsonl(
                input_path=os.path.join(output_path, '.cleaned'),
                output_path=os.path.join(output_path, 'out'),
                keep_text_only=True,
                source_tag=output_source_value
            )
            global_logger.log_text(f"Final data dir: {os.path.join(output_path, 'out')}")
        else:
            process_work_single_thread(
                work_path=work_path, 
                output_path=os.path.join(output_path, '.cleaned'), 
                text_key=input_text_key
            )
            dump_jsonls2jsonl(
                input_path=os.path.join(output_path, '.cleaned'),
                output_path=os.path.join(output_path, 'out'),
                keep_text_only=True,
                source_tag=output_source_value
            )
            global_logger.log_text(f"Final data dir: {os.path.join(output_path, 'out/tmp.jsonl')}")

        # if clean or filter is in the process, deduplicatior is in the process
        if settings['if_dedup']:
            dedupicator_module = Deduplicator(settings)
            dedupicator_module.dedup()
            global_logger.log_text(f"Deduplicated data dir: {os.path.join(output_path, 'out/dedup.jsonl')}")

def sample_compare_results(settings: dict):
    '''
    step 5: sample few texts from raw data and clean them only by cleaner
    '''
    input_path, input_ext, input_text_key, output_path, output_source_value = settings['input_path'], settings['input_ext'], settings['input_text_key'], settings['output_path'], settings['output_source_value']
    work_path = prepare_works(os.path.join(output_path, '.tmp'), input_ext)

    sampler_config = {'input_path': work_path,
        'output_path': os.path.join(output_path, 'presentation.jsonl'),
        'if_sample_randomly': True,
        'SAMPLE_RANDOMLY_NUM': 10}
    sampler = Sampler(SampleConfig(sampler_config))
    sampler.sample_randomly_works()

    # load settings for modules
    modulemanager.load_modules(settings=settings)

    # we need to compare the difference of raw and refined texts
    settings['if_filter'] = False
    process_work_single_thread(
        work_path=os.path.join(output_path, 'presentation.jsonl'), 
        output_path=os.path.join(output_path, '.sample_cleaned'), 
        text_key=input_text_key
    )
    dump_jsonls2jsonl(
        input_path=os.path.join(output_path, '.sample_cleaned'),
        output_path=os.path.join(output_path, 'sample_cleaned'),
        keep_text_only=True,
        source_tag=output_source_value
    )
    global_logger.log_text(f"Final data dir: {os.path.join(output_path, 'sample_cleaned/tmp.jsonl')}")


def process_work(conf: Settings, option: int=0):
    '''
    @param: 
        option: 
            0: the whole process
            1: only prepare works, sample and debug (before the refined pipline)
            2: clean, filter, deduplication, sample and debug, sample comparing results（the refined pipline）
    '''
    settings = conf.settings
    input_path, input_ext, input_text_key, output_path, output_source_value = settings['input_path'], settings['input_ext'], settings['input_text_key'], settings['output_path'], settings['output_source_value']

    # load settings for modules
    modulemanager.load_modules(settings=settings)

    # nothing to do, warning user
    if not(settings['if_debug'] or settings['if_clean'] or settings['if_filter'] or settings['if_dedup']):
        warning_str = 'Nothing to do, please make sure some options become \'true\' in your setting file.'
        global_logger.log_text(warning_str)
        return {'warning': warning_str}
    
    if option == 1:
        # if option == and do not debug, the solution is in app.py (do not display the information of debugger)
        if settings['if_debug']:
            prepare_jsonl_files(settings)
            sample_debug(settings, 'raw')
            # only debug, warning user
            if not(settings['if_clean'] or settings['if_filter'] or settings['if_dedup']):
                warning_str = 'Only debug, please make sure some options become \'true\' in your setting file.'
                global_logger.log_text(warning_str)
                return {'warning': warning_str}
        with open(os.path.join(output_path, 'bound.json'), 'w') as fw:
            json.dump(modulemanager.filter_module.filter_ops["FilterPassageByPPL"].ppl_filter_thresholds, fw)
    
    elif option == 2: 
        # 前端需要处理一下这个部分，如果返回了warning_str，就不显示之后的按钮，只显示warning_str和返回主页面的按钮
        if not(settings['if_clean'] or settings['if_filter'] or settings['if_dedup']):
            warning_str = 'No cleaner, filter and deduplicator, please make sure some options become \'true\' in your setting file.'
            global_logger.log_text(warning_str)
            return {'warning': warning_str}
        # if not debug, the jsonl files don't be prepared
        if settings['if_debug'] == False:
            prepare_jsonl_files(settings)
        refining_process(settings)
        if settings['if_debug']:        
            sample_debug(settings, 'refined')
        # if no cleaner and no filter, sample_compare_results should not be executed
        if settings['if_clean'] or settings['if_filter']:
            sample_compare_results(settings)
        else:
            return {'if_compare': False}
        
        bound_path = os.path.join(output_path, 'bound.json')
        if os.path.exists(bound_path):
            os.remove(bound_path)
        

    # preserved the way to execute the entire process using the python command
    elif option == 0:
        # if option == and do not debug, the solution is in app.py (do not display the information of debugger)
        if settings['if_debug']:
            prepare_jsonl_files(settings)
            sample_debug(settings, 'raw')
            # only debug, warning user
            if not(settings['if_clean'] or settings['if_filter'] or settings['if_dedup']):
                warning_str = 'Only debug, please make sure some options become \'true\' in your setting file.'
                global_logger.log_text(warning_str)
                return {'warning': warning_str}
        if not(settings['if_clean'] or settings['if_filter'] or settings['if_dedup']):
            warning_str = 'No cleaner, filter and deduplicator, please make sure some options become \'true\' in your setting file.'
            global_logger.log_text(warning_str)
            return {'warning': warning_str}
        # if not debug, the jsonl files don't be prepared
        if settings['if_debug'] == False:
            prepare_jsonl_files(settings)
        refining_process(settings)
        if settings['if_debug']:        
            sample_debug(settings, 'refined')
        # # if no cleaner and no filter, sample_compare_results should not be executed
        # if settings['if_clean'] or settings['if_filter']:
        #     sample_compare_results(settings)
        # else:
        #     return {'if_compare': False}

