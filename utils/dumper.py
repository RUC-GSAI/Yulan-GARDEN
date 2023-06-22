import os
import json
from tqdm import tqdm

from utils.utils import prepare_works

def dump_jsonl(path: str, data, encoding='utf-8', source_tag='.tmp') -> None:
    try:
        with open(path, mode='a', encoding=encoding) as fw:
            for line in data:
                ndic = {"text": line, "source": source_tag}
                fw.write(json.dumps(ndic, ensure_ascii=False) + '\n')
    except Exception as ne:
        print(f"bad file {path} for exception {ne}")

def dump_txts2jsonl(input_path, output_path, encoding='utf-8', source_tag='.tmp') -> None:
    txt_works = prepare_works(input_path=input_path, input_ext='txt')
    with open(os.path.join(output_path, 'tmp.jsonl'), mode='a', encoding=encoding) as fw:
        for txt_work in txt_works:
            with open(txt_work, mode='r', encoding=encoding) as fr:
                text = fr.read()
                fw.write(json.dumps({"text": text, "source": source_tag}, ensure_ascii=False) + '\n')

def dump_jsonls2jsonl(input_path, output_path, keep_text_only=False, encoding='utf-8', source_tag='.tmp') -> None:
    jsonl_works = prepare_works(input_path=input_path, input_ext='jsonl')
    with open(os.path.join(output_path, 'tmp.jsonl'), mode='a', encoding=encoding) as fw:
        for txt_work in tqdm(jsonl_works, desc="dumper"):
            with open(txt_work, mode='r', encoding=encoding) as fr:
                for line in fr:
                    meta = json.loads(line)
                    if keep_text_only:
                        meta = {"text": meta['text'], "source": source_tag}
                    else:
                        if 'source' not in meta.keys(): meta['source'] = source_tag
                    fw.write(json.dumps(meta, ensure_ascii=False) + '\n')