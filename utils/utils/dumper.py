import os
import json
from tqdm import tqdm
from bs4 import BeautifulSoup
import mobi
import shutil
from urllib.parse import unquote
import zipfile
import lzma

from utils.utils import prepare_works

def dump_data2jsonl(path: str, data: list, keep_text_only=False, text_key="text", mode='w', encoding='utf-8', source_tag='.tmp') -> None:
    try:
        with open(path, mode=mode, encoding=encoding) as fw:
            for line in data:
                if type(line) is dict:
                    if keep_text_only:
                        line["source"] = source_tag
                        ndic = line
                    else:
                        ndic = line
                else:
                    continue
                fw.write(json.dumps(ndic, ensure_ascii=False) + '\n')
    except Exception as ne:
        print(f"bad file {path} for exception {ne}")

def dump_txts2jsonl(input_path, output_path, mode='w', encoding='utf-8', source_tag='.tmp') -> None:
    if not os.path.exists(output_path): os.makedirs(output_path, exist_ok=True)
    txt_works = prepare_works(input_path=input_path, input_ext='txt')
    with open(os.path.join(output_path, 'tmp.jsonl'), mode=mode, encoding=encoding) as fw:
        for txt_work in txt_works:
            with open(txt_work, mode='r', encoding=encoding, errors='ignore') as fr:
                text = fr.read()
                fw.write(json.dumps({"text": text, "source": source_tag}, ensure_ascii=False) + '\n')

def dump_mobi2jsonl(input_path, output_path, mode='w', encoding='utf-8', source_tag='.tmp') -> None:
    if not os.path.exists(output_path): os.makedirs(output_path, exist_ok=True)
    mobi_works = prepare_works(input_path=input_path, input_ext='mobi')
    with open(os.path.join(output_path, 'tmp.jsonl'), mode=mode, encoding=encoding) as fw:
        for mobi_work in mobi_works:
            try:
                tempdir, filepath = mobi.extract(mobi_work)
            except:
                continue
            with open(filepath, 'rb') as mobi_fp:
                text = mobi_fp.read()
            shutil.rmtree(tempdir)
            soup = BeautifulSoup(text, 'html.parser')
            soup = soup.prettify()
            soup = BeautifulSoup(soup, 'html.parser')
            text = soup.get_text().strip()
            fw.write(json.dumps({"text": text, "source": source_tag}, ensure_ascii=False) + '\n')

def dump_epub2jsonl(input_path, output_path, mode='w', encoding='utf-8', source_tag='.tmp') -> None:
    if not os.path.exists(output_path): os.makedirs(output_path, exist_ok=True)
    epub_works = prepare_works(input_path=input_path, input_ext='epub')

    with open(os.path.join(output_path, 'tmp.jsonl'), mode=mode, encoding=encoding) as fw:
        for epub_work in epub_works:
            try:
                book = zipfile.ZipFile(epub_work)
            except:
                continue
            xhtml_data = [string for string in book.namelist() if
                string.endswith('xhtml') or string.endswith('html') or string.endswith('xml')]         
            text = ''
            for k in range(len(xhtml_data)):
                try:
                    chapter_file = book.open(unquote(xhtml_data[k]))
                    chapter_content = chapter_file.read().decode('utf-8')
                    chapter_content = BeautifulSoup(chapter_content, 'html')
                    text += chapter_content.get_text().strip()
                except:
                    break
            fw.write(json.dumps({"text": text, "source": source_tag}, ensure_ascii=False) + '\n')

def dump_txtxz2jsonl(input_path, output_path, mode='w', encoding='utf-8', source_tag='.tmp') -> None:
    if not os.path.exists(output_path): os.makedirs(output_path, exist_ok=True)
    txtxz_works = prepare_works(input_path=input_path, input_ext='txt.xz')
    with open(os.path.join(output_path, 'tmp.jsonl'), mode=mode, encoding=encoding) as fw:
        for txtxz_work in txtxz_works:
            with lzma.open(txtxz_work, mode='rb') as fr:
                line = fr.readline()
                while line:
                    line = extract_text(line, source_tag)
                    if line is not None and line['text'] is not None:
                        fw.write(json.dumps(line, ensure_ascii=False) + '\n')
                    line = fr.readline()

def dump_jsonls2jsonl(input_path, output_path, keep_text_only=False, mode='w', encoding='utf-8', source_tag='.tmp') -> None:
    if not os.path.exists(output_path): os.makedirs(output_path, exist_ok=True)
    jsonl_works = prepare_works(input_path=input_path, input_ext='jsonl')
    if len(jsonl_works) == 1:
        command_line = f"cp {jsonl_works[0]} {os.path.join(output_path, 'tmp.jsonl')}"
        os.system(command_line)
    else:
        with open(os.path.join(output_path, 'tmp.jsonl'), mode=mode, encoding=encoding) as fw:
            for txt_work in tqdm(jsonl_works, desc="dumper"):
                with open(txt_work, mode='r', encoding=encoding) as fr:
                    for line in fr:
                        meta = json.loads(line)
                        if keep_text_only:
                            meta['source'] = source_tag
                        else:
                            if 'source' not in meta.keys(): meta['source'] = source_tag
                        fw.write(json.dumps(meta, ensure_ascii=False) + '\n')

def extract_text(raw_page, source_tag='.tmp'):
    decoded_page = raw_page.decode('gbk', errors='ignore')
    try:
        utf8_page = json.loads(decoded_page)
        raw_content = utf8_page['content']
        soup = BeautifulSoup(raw_content, features='html.parser')
        all_spans = soup.find_all('span')
        filtered_spans = []
        for span in all_spans:
            if ('class' in span.attrs) and ('rich_media_meta' in span.attrs['class'] or 'profile_meta_value' in span.attrs['class']):
                continue
            filtered_spans.append(span)
        all_span_text = [_.get_text() for _ in filtered_spans]
        cleaned_content = '\n'.join(all_span_text)
        # return {
        #     '_id': utf8_page['_id'],
        #     'url': utf8_page['url'],
        #     'title': utf8_page['title'],
        #     'ts': utf8_page['ts'],
        #     'content': cleaned_content
        # }
        biz = utf8_page['url'].split('biz=')[1].split('&')[0]
        return {
            'text': cleaned_content,
            'source': source_tag,
            'meta': {
                'biz': biz
            }
        }
    except:
        return None
