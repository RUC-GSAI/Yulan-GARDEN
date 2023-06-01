import os
import json

from utils.workers import *

def dump_jsonl(path: str, data, encoding='utf-8', source_tag='.tmp') -> None:
    try:
        with open(path, mode='a', encoding='utf-8') as fw:
            for line in data:
                ndic = {"text": line, "source": source_tag}
                fw.write(json.dump(ndic, ensure_ascii=False) + '\n')
    except Exception as ne:
        print(f"bad file {path} for exception {ne}")

def dump_txts2jsonl(input_path, output_path, encoding='utf-8', source_tag='.tmp') -> None:
    txt_works = prepare_works(input_path=input_path, input_ext='txt')
    with open(os.path.join(output_path, 'tmp.jsonl'), mode='a', encoding=encoding) as fw:
        for txt_work in txt_works:
            with open(txt_work, mode='r', encoding=encoding) as fr:
                text = fr.read()
                fw.write(json.dump({"text": text, "source": source_tag}, ensure_ascii=False) + '\n')

def dump_jsonls2jsonl(input_path, output_path, encoding='utf-8', source_tag='.tmp') -> None:
    txt_works = prepare_works(input_path=input_path, input_ext='jsonl')
    with open(os.path.join(output_path, 'tmp.jsonl'), mode='a', encoding=encoding) as fw:
        for txt_work in txt_works:
            with open(txt_work, mode='r', encoding=encoding) as fr:
                for line in fr:
                    meta = json.loads(line)
                    if 'source' not in meta.keys(): meta['source'] = source_tag
                    fw.write(json.dump(meta, ensure_ascii=False) + '\n')