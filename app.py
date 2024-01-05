import os
import json
from flask import Flask, render_template, request, send_from_directory, session, redirect, url_for
from datetime import timedelta
from utils.quick_start import run_zhem
from time import sleep, time
import threading
import jsonlines
from utils.utils.logger import Logger
from utils.retriever.elasticobj import ElasticObj

from fastapi import FastAPI, Form
import uvicorn as u
from starlette.requests import Request
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
import datetime


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, timedelta):
            return str(obj)
        # 其他需要处理的类型
        return super().default(obj)


def get_data_names(refined_data_path):
    '''
    get all data names from refined_data_path
    '''
    try:
        with open(refined_data_path, 'r') as fr:
            refined_data = json.load(fr)
    except:
        refined_data = {}
    finally:
        # all exists data names
        return set(refined_data.keys())


def read_data(rfile):
    '''
    for ElasticObj to read data
    '''
    if rfile.endswith('.json'):
        with open(rfile, 'r') as f:
            data = json.load(f)
    elif rfile.endswith('.jsonl'):
        with jsonlines.open(rfile) as reader:
            data = []
            for obj in reader:
                data.append(obj)
    return data


def load_parameter_definitions(example_path):
    '''
    load example config (to create new config from example)
    '''
    with open(example_path, 'r') as file:
        parameter_definitions = json.load(file)
    return parameter_definitions


def get_settings_files(settings_folder):
    '''
    get all existing settings from settings_folder
    '''
    settings_files = [f for f in os.listdir(settings_folder) if f.endswith('.json')]
    return settings_files


def jsonl2lines(input_path, input_text_key):
    '''
    transfer jsonl to text lines
    '''
    lines = []
    with open(input_path) as fr:
        for line in fr:
            lines.append(json.loads(line)[input_text_key])    
    return lines


def get_files_in_folder(folder_path):
    file_list = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_list.append(file_path)
    return file_list


def access_nested_dict(data, keys, new_value=None):
    '''
    修改嵌套字典的值
    '''
    if len(keys) == 0 or new_value is None or new_value == '':
        return data
    key = keys[0]
    # 递归终止
    if len(keys) == 1:
        if key in data:
            data[key] = _type_conversion(new_value, type(data[key]))
        else:
            return
    if key in data:
        access_nested_dict(data[key], keys[1:], new_value)


def _type_conversion(value, target_type):
    if target_type == bool:
        return bool(value)
    elif target_type == int:
        return int(value)
    elif target_type == float:
        return float(value)
    elif target_type == str:
        return str(value)
    elif target_type == dict:
        pairs = value.strip().split(';')
        ret = {}
        for pair in pairs:
            key, value = pair.split(':')
            ret[key] = value
        return ret
        # return eval(value)
    elif target_type == list:
        return value.strip().split(' ') 
    else:
        return value


# this function can't be used because of no elasticsearch engine in this machine
def create_ElasticObj_index(config, data_type):
    '''
    create ElasticObj and index
    '''
    assert data_type == '_raw' or data_type == '_refined', f'data_type should be \'_raw\' or \'_refined\', {data_type} is not allowed.'
    obj = ElasticObj(index_name=config['output_source_value'].lower() + data_type)
    print(obj.es)
    obj.create_index(obj.index_name)
    if data_type == '_refined':
        ### --------- 读文件 ---------
        print(f"Reading file {config['output_path']}...")
        t1 = time()
        if config['if_dedup']:
            data = read_data(os.path.join(config['output_path'], 'out/dedup.jsonl'))
        else:
            data = read_data(os.path.join(config['output_path'], 'out/tmp.jsonl'))
    else:
        ### --------- 读文件 ---------
        print(f"Reading file {config['input_path']}...")
        t1 = time()
        if config['if_dedup']:
            data = read_data(config['input_path'])
        else:
            data = read_data(config['input_path'])
    print("Read time: {:.2f}s".format(time()-t1))
    total_num = len(data)
    print("%s items loaded." % total_num)
    t2 = time()
    obj.bulk_Index_Data(data) # 20w/min; 6k-1.44s; 270k-77s
    print("Insert time: {:.2f}s".format(time()-t2))


# this function can't be used because of no elasticsearch engine in this machine
def query_arxiv(text, qtype, data_type):
    '''
    query -> retrieved results
    '''
    _candidates = []

    _doc = {
        "query": {
            "multi_match": {
                # "default_field": "abstract",
                "query": "",
                "fields": ["text"]
            }
        }
    }
    _doc['query']['multi_match']['query'] = text
    _doc['size'] = 50 # 最多返回50条
    globals()[f'es_obj_{qtype}{data_type}'] = ElasticObj(index_name=f'{qtype}{data_type}')
    hits = globals()[f'es_obj_{qtype}{data_type}'].Get_Data_By_Body(_doc)

    for hit in hits:
        candidate = {}
        candidate["text"] = hit["_source"]["text"]
        # candidate["source"] = hit["_source"]["source"]
        candidate["score"] = hit["_score"]
        _candidates.append(candidate)

    return _candidates


def add_data_information(refined_data_path, config):
    '''
    add data imformation (know about the input_path and output_path of all the refined data)
    '''
    if not os.path.exists(refined_data_path):
        with open(refined_data_path, 'w') as fw:
            fw.write('{}')
    with open(refined_data_path, 'r') as fr:
        refined_data = json.load(fr)
    if refined_data == None:
        refined_data = {}
    # 'output_source_value' is dataset name
    data_name = config['output_source_value'].lower()
    if data_name in refined_data:
        refined_data[data_name].append({'input_path': config['input_path'], 'output_path': config['output_path']})
    else:
        refined_data[data_name] = [{'input_path': config['input_path'], 'output_path': config['output_path']}]
    with open(refined_data_path, 'w') as fw:
        json.dump(refined_data, fw, indent=4, ensure_ascii=False)    

# no use in new version
def retrieve(retriever_source, key_words):
    '''
    for debug
    '''
    texts = ['I am a robot', 'ZHEM: A Synthetic Data Processing Pipeline for Large Language Models', '存在的问题：直到清洗完成后页面才会完成跳转，希望在清洗时展示一个“清洗中”的页面，清洗结束后展示“清洗以完成”的页面', '比较 oasis, data-juicer 和我们工作的优劣', '对统一cleaner进行单元测试，添加email/phone/ip/idcard等预定义清洗算子；开始拆解filter，删除meta算子']
    return texts

# no use in new version
def process_data():
    '''
    for debug
    '''
    for i in range(10):
        sleep(1)
        logger.log_text('{}: for test\n'.format(i))

# no use
def sample(input_path, sample_length=10):
    '''
    sample texts from sampler
    '''

    '''
    for debug
    '''
    origin_texts = ['I am a robo\pt', 'ZHE M: A Synthetic\n Data Processing Pipeline for Large Language Models', '  - 存在的问题：直到清洗完成后页面才会完成跳转? ? ，希望在清洗时展示一个“清洗中”的页面，清洗结束后展示“清洗以完成”的页面', '  [] 比较 oasis, data-juicer 和我们工作的优劣', '对统一cleaner进行单元测试，添加email/phone/ip/idcard等预定义清洗算子；开始拆解filter，删除meta算子']
    refined_texts = ['I am a robot', 'ZHEM: A Synthetic Data Processing Pipeline for Large Language Models', '存在的问题：直到清洗完成后页面才会完成跳转，希望在清洗时展示一个“清洗中”的页面，清洗结束后展示“清洗以完成”的页面', '比较 oasis, data-juicer 和我们工作的优劣', '对统一cleaner进行单元测试，添加email/phone/ip/idcard等预定义清洗算子；开始拆解filter，删除meta算子']
    return list(zip(*[origin_texts, refined_texts]))



app = Flask(__name__)
app.secret_key = '123'
'''
    session variables:
        session['retriever_source']: for /retriever return to /show_config ('input_path') or /processing ('output_path')
        session['config_name']: name of the config
'''
processing_done = threading.Event()
# 获取settings文件夹下的所有配置文件列表
settings_folder = 'settings'
log_path = 'process.log'
tmp_folder = 'tmp'
# {dataset name: [{'input_path': config['input_path'], 'output_path': config['output_path']}]}
refined_data_path = 'refined_data.json'
example_path = 'settings/example.json'
data_names = get_data_names(refined_data_path)
logger = Logger()
# app.mount("/static", StaticFiles(directory="static"), name="static")
# 将自定义的JSON编码器类设置为app的json_encoder
app.json_encoder = CustomJSONEncoder



@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


# page: select an existing config
@app.route('/select_config', methods=['GET', 'POST'])
def select_config():
    return render_template('select_config.html', settings_files=get_settings_files(settings_folder))


# page: customize a config
@app.route('/customize_config', methods=['POST'])
def customize_config():
    return render_template('customize_config.html', parameter_definitions=load_parameter_definitions(example_path))


# page: show config and submit task
@app.route('/show_config', methods=['POST'])
def show_config():
    if request.method == 'POST':
        # clear the log
        with open(log_path, 'w') as fw:
            pass
        select_config = request.form.get('select_config')
        custom_file = request.form.get('custom_config')
        retrever_back = request.form.get('retrever_back')
        if select_config:            
            # 如果选择了已有配置文件，则读取该文件并展示给用户
            with open(os.path.join(settings_folder, select_config)) as fr:
                config = json.load(fr)
                session['retriever_source'] = 'input_path'

            ### ------------------ es ------------------
            # create_ElasticObj_index(config=config, data_type='_raw')
            ### ------------------ es ------------------
            data_names.add(config['output_source_value'].lower())

            zhem_ret_args = run_zhem(os.path.join(settings_folder, session['config_name']), 1, 1)   

            if config['if_debug']:
                # figs_list = get_files_in_folder(os.path.join(config['output_path'], 'figs/'))
                figs_list = get_files_in_folder('static/figs/')
                with open(config['debug_paras']['debug_report_path'], 'r') as fr:
                    debug_file = json.load(fr)
                ret_args = {'if_debug': True, 'debug_path': config['debug_paras']['debug_report_path'], 'figs_list': figs_list, 'debug_file': json.dumps(debug_file, indent=4, ensure_ascii=False)}
            else:
                ret_args = {'if_debug': False}   
            # # sample texts from 'input_path', return the sample list and refined list
            # sample_results = sample(config['input_path'])
            if zhem_ret_args and 'warning' in zhem_ret_args:                
                ret_args['warning'] = zhem_ret_args['warning']

            # save the temp results
            with open(os.path.join(tmp_folder, 'ret_args.json'), 'w') as fw:
                json.dump(ret_args, fw, indent=4)

            # 使用json格式化展示配置信息
            config_formatted = json.dumps(config, indent=4, ensure_ascii=False)
            # 将config的名字保存，便于processing访问
            session['config_name'] = select_config
            return render_template('show_config.html', config=config_formatted, ret_args=ret_args)  
        
        elif custom_file:
            # 如果选择了自定义配置文件，则从表单中获取各个参数的值，并保存为新的配置文件
            config = load_parameter_definitions(example_path)
            session['retriever_source'] = 'input_path'
            for key, value in request.form.items():
                keys = key.split('.')          
                access_nested_dict(config, keys, value)

            ### ------------------ es ------------------
            # create_ElasticObj_index(config=config, data_type='_raw')
            ### ------------------ es ------------------
            data_names.add(config['output_source_value'].lower())

            # 生成一个配置文件名，并将该文件保存到settings文件夹下
            new_config_file = custom_file + '.json'
            with open(os.path.join(settings_folder, new_config_file), 'w') as fr:
                json.dump(config, fr, indent=4)
            # 使用json格式化展示配置信息
            config_formatted = json.dumps(config, indent=4, ensure_ascii=False)
            # 将config的名字保存，便于processing访问
            session['config_name'] = new_config_file            
            return render_template('show_config.html', config=config_formatted, parameter_definitions=load_parameter_definitions(example_path))     
        elif retrever_back:
            # 如果选择了已有配置文件，则读取该文件并展示给用户
            with open(os.path.join(settings_folder, session['config_name'])) as fr:
                config = json.load(fr)
            # 使用json格式化展示配置信息
            config_formatted = json.dumps(config, indent=4, ensure_ascii=False)
            with open(os.path.join(tmp_folder, 'ret_args.json'), 'r') as fr:
                ret_args = json.load(fr)
            return render_template('show_config.html', config=config_formatted, ret_args=ret_args)  
    return render_template('show_config.html')


@app.route('/retriever', methods=['POST', 'GET'])
def retriever():
    if request.method == 'POST':
        retreve_task = request.form.get('retrieve_task')
        if retreve_task:            
            return render_template('retriever.html', data_names=data_names, source=session['retriever_source'])
    return render_template('retriever.html', data_names=data_names)
    

@app.route('/text_search/', methods=['POST'])
def read_text():
    if request.method == 'POST':
        qtype = request.args.get("qtype")
        query = request.form.get('query')
        print("qtype:", qtype)
        t1 = time()
        data_type = '_raw' if session['retriever_source'] == 'input_path' else '_refined'
        res = query_arxiv(query, qtype, data_type)
        time_cost = round(time() - t1, 3)
        n = len(res)
        # 打印当前时间的query
        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(now_time + " _Query_: " + query)
        
        for item in res:
            item['score'] = round(item['score'], 3)
        if not n:
            return render_template("no_results.html")
        else:
            return render_template("results.html",
                                    query=query,
                                    N=n,
                                    cost_time=time_cost,
                                    res=res
                                    )


@app.route('/processing', methods=['POST'])
def processing():
    if request.method == 'POST':
        session['retriever_source'] = 'output_path'
        # from page: processing
        confirm = request.form.get('confirm')
        # from page: retriever
        retrever_back = request.form.get('retrever_back')
        if confirm:
            # # data refined process
            # process_data()
            zhem_ret_args = run_zhem(os.path.join(settings_folder, session['config_name']), 1, 2)         
            with open(os.path.join(settings_folder, session['config_name']), 'r') as fr:
                config = json.load(fr)
            if config['if_debug']:
                # figs_list = get_files_in_folder(os.path.join(config['output_path'], 'figs/'))
                figs_list = get_files_in_folder('static/figs/')
                with open(config['debug_paras']['debug_report_path'], 'r') as fr:
                    debug_file = json.load(fr)
                ret_args = {'if_debug': True, 'debug_path': config['debug_paras']['debug_report_path'], 'figs_list': figs_list, 'debug_file': json.dumps(debug_file, indent=4, ensure_ascii=False)}
            else:
                ret_args = {'if_debug': False}   
            # # sample texts from 'input_path', return the sample list and refined list
            # sample_results = sample(config['input_path'])
            if zhem_ret_args == None or 'if_compare' not in zhem_ret_args:
                origin_texts = jsonl2lines(os.path.join(config['output_path'], 'presentation.jsonl'), config['input_text_key'])
                refined_texts = jsonl2lines(os.path.join(config['output_path'], 'sample_cleaned/tmp.jsonl'), config['input_text_key'])
                ret_args['sample_results'] = list(zip(*[origin_texts, refined_texts]))

            # save the temp results
            with open(os.path.join(tmp_folder, 'ret_args.json'), 'w') as fw:
                json.dump(ret_args, fw, indent=4)
            # with open(os.path.join(tmp_folder, 'sample_results.json'), 'w') as fw:
            #     json.dump(sample_results, fw, indent=4)

            # # add data imformation (know about the input_path and output_path of all the refined data)
            add_data_information(refined_data_path, config)
            ### ------------------ es ------------------
            # create_ElasticObj_index(config=config, data_type='_refined')
            ### ------------------ es ------------------

            return render_template('processing.html', ret_args=ret_args, source=session['retriever_source'])
        
        if retrever_back:
            with open(os.path.join(settings_folder, session['config_name']), 'r') as fr:
                config = json.load(fr)

            # load the temp results
            with open(os.path.join(tmp_folder, 'ret_args.json'), 'r') as fr:
                ret_args = json.load(fr)
            with open(os.path.join(tmp_folder, 'sample_results.json'), 'r') as fr:
                sample_results = json.load(fr)

            return render_template('processing.html', ret_args=ret_args, sample_results=sample_results, source=session['retriever_source'])
    return render_template('processing.html')


@app.route('/read_log', methods=['POST'])
def read_log():
    # 处理log文件的内容，并返回响应
    # 例如从文件中读取内容
    with open(log_path, 'r') as fr:        
        log_content = fr.read()
    return log_content


@app.template_filter('is_dict')
def is_dict(value):
    return isinstance(value, dict)


@app.template_filter('is_list')
def is_list(value):
    return isinstance(value, list)


if __name__ == '__main__':
    app.run(debug=True)