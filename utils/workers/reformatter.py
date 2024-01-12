from utils.utils.dumper import *
from utils.rules import *

def reformat_everything2jsonl(input_ext: str, input_path: str, output_path: str, output_source_value: str):
    if input_ext in TXT_SUFFIX:
        dump_txts2jsonl(
            input_path=input_path, 
            output_path=output_path, 
            source_tag=output_source_value
        )
    elif input_ext in JSONL_SUFFIX:
        dump_jsonls2jsonl(
            input_path=input_path, 
            output_path=output_path, 
            keep_text_only=False,
            source_tag=output_source_value
        )
    elif input_ext in EPUB_SUFFIX:
        dump_epub2jsonl(
            input_path=input_path, 
            output_path=output_path, 
            source_tag=output_source_value
        )
    elif input_ext in TXTXZ_SUFFIX:
        dump_txtxz2jsonl(
            input_path=input_path, 
            output_path=output_path, 
            source_tag=output_source_value
        )    