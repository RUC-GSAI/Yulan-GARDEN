import os
import json
from flask import Flask, render_template, request, send_from_directory, session, redirect, url_for
from datetime import timedelta
from utils.quick_start import run_zhem
from time import sleep
import threading
import logging
import difflib
from utils.utils.logger import Logger


app = Flask(__name__)
app.secret_key = '123'
'''
    session variables:
        session['retrever_source']: for /retriever return to /show_config ('input_path') or /processing ('output_path')
        session['config_name']: name of the config
'''
processing_done = threading.Event()
# 获取settings文件夹下的所有配置文件列表
settings_folder = 'settings'
log_path = 'process.log'
refined_data_path = 'refined_data.json'
logger = Logger()


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, timedelta):
            return str(obj)
        # 其他需要处理的类型
        return super().default(obj)

# 将自定义的JSON编码器类设置为app的json_encoder
app.json_encoder = CustomJSONEncoder


def load_parameter_definitions():
    with open('settings/example.json', 'r') as file:
        parameter_definitions = json.load(file)
    # print(parameter_definitions['if_parallel'])
    # print(parameter_definitions['parallel_paras']['if_cut'])
    return parameter_definitions


def get_settings_files():
    settings_files = [f for f in os.listdir(settings_folder) if f.endswith('.json')]
    return settings_files


# 修改嵌套字典的值
def access_nested_dict(data, keys, new_value=None):
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


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


# page: select an existing config
@app.route('/select_config', methods=['GET', 'POST'])
def select_config():
    return render_template('select_config.html', settings_files=get_settings_files())


# page: customize a config
@app.route('/customize_config', methods=['POST'])
def customize_config():
    return render_template('customize_config.html', parameter_definitions=load_parameter_definitions())


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
                session['retrever_source'] = 'input_path'
            # 使用json格式化展示配置信息
            config_formatted = json.dumps(config, indent=4, ensure_ascii=False)
            # 将config的名字保存，便于processing访问
            session['config_name'] = select_config
            # 检索路径，此时为input_path
            return render_template('show_config.html', config=config_formatted)       
        elif custom_file:
            # 如果选择了自定义配置文件，则从表单中获取各个参数的值，并保存为新的配置文件
            config = load_parameter_definitions()
            session['retrever_source'] = 'input_path'
            for key, value in request.form.items():
                keys = key.split('.')          
                access_nested_dict(config, keys, value)
            # 生成一个配置文件名，并将该文件保存到settings文件夹下
            new_config_file = custom_file + '.json'
            with open(os.path.join(settings_folder, new_config_file), 'w') as fr:
                json.dump(config, fr, indent=4)
            # 使用json格式化展示配置信息
            config_formatted = json.dumps(config, indent=4, ensure_ascii=False)
            # 将config的名字保存，便于processing访问
            session['config_name'] = new_config_file            
            return render_template('show_config.html', config=config_formatted, parameter_definitions=load_parameter_definitions())     
        elif retrever_back:
            # 如果选择了已有配置文件，则读取该文件并展示给用户
            with open(os.path.join(settings_folder, session['config_name'])) as fr:
                config = json.load(fr)
            # 使用json格式化展示配置信息
            config_formatted = json.dumps(config, indent=4, ensure_ascii=False)
            return render_template('show_config.html', config=config_formatted)  
    return render_template('show_config.html')


def retrieve(retrever_source, key_words):
    '''
    for debug
    '''
    texts = ['I am a robot', 'ZHEM: A Synthetic Data Processing Pipeline for Large Language Models', '存在的问题：直到清洗完成后页面才会完成跳转，希望在清洗时展示一个“清洗中”的页面，清洗结束后展示“清洗以完成”的页面', '比较 oasis, data-juicer 和我们工作的优劣', '对统一cleaner进行单元测试，添加email/phone/ip/idcard等预定义清洗算子；开始拆解filter，删除meta算子']
    return texts


# page: retriever
@app.route('/retriever', methods=['POST'])
def retriever():
    if request.method == 'POST':
        retreve_task = request.form.get('retreve_task')
        if retreve_task:
            key_words = request.form.get('key_words')
            with open(os.path.join(settings_folder, session['config_name']), 'r') as fr:
                config = json.load(fr)
            # session['retrever_source'] is 'input_path' or 'output_path'
            texts = retrieve(config[session['retrever_source']], key_words.split(' '))
            return render_template('retriever.html', texts=texts, source=session['retrever_source'])
    return render_template('retriever.html')


def process_data():
    '''
    for debug
    '''
    for i in range(10):
        sleep(1)
        logger.log_text('{}: for test\n'.format(i))


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


@app.route('/processing', methods=['POST'])
def processing():
    if request.method == 'POST':
        with open(os.path.join(settings_folder, session['config_name']), 'r') as fr:
            config = json.load(fr)
        if config['if_debug']:
            with open(config['debug_paras']['debug_report_path'], 'r') as fr:
                debug_file = json.load(fr)
            ret_args = {'if_debug': True, 'debug_path': config['debug_paras']['debug_report_path'],  'debug_file': json.dumps(debug_file, indent=4, ensure_ascii=False)}
        else:
            ret_args = {'if_debug': False}
        session['retrever_source'] = 'output_path'
        # from page: processing
        confirm = request.form.get('confirm')
        # from page: retriever
        retrever_back = request.form.get('retrever_back')
        if confirm:
            # # data refined process
            # process_data()
            run_zhem(os.path.join(settings_folder, session['config_name']), 1)            
            # sample texts from 'input_path', return the sample list and refined list
            sample_results = sample(config['input_path'])
            # add data imformation (know about the input_path and output_path of all the refined data)
            if not os.path.exists(refined_data_path):
                with open(refined_data_path, 'w') as fw:
                    fw.write('{}')
            with open(refined_data_path, 'r') as fr:
                refined_data = json.load(fr)
            if refined_data == None:
                refined_data = {}
            refined_data[config['input_path']] = config['output_path']
            with open(refined_data_path, 'w') as fw:
                json.dump(refined_data, fw, indent=4, ensure_ascii=False)            
            
            sleep(4)
            return render_template('processing.html', ret_args=ret_args, sample_results=sample_results, source=session['retrever_source'])
        
        if retrever_back:
            sample_results = sample(config['input_path'])
            return render_template('processing.html', ret_args=ret_args, sample_results=sample_results, source=session['retrever_source'])
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
    app.run(debug=True, port=8080)