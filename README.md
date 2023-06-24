# ZHEM

## Introduction

ZHEM is a Chinese(ZH-*, like zh-cn, zh-tw and so on) Natural Language data Processing Pipeline for pretraining Large Language Models(LLMs), developed by [@Emanual20](https://github.com/Emanual20) and [@PhealenWang](https://github.com/PhealenWang) from Renmin University of China, supervised by [@defaultstr](https://github.com/defaultstr).

The target datasets of this pipeline are mainly larger than 100GB. Time cost will be prohibitively long when only single process is used. As a result, we introduced multi-processing to this pipeline.

Since the nodes for processing data, the optimized parameter of filter rules and the cleaning demands(Whether the raw data contains <html> label? Which regular expressions should be used?) may vary to a large extent among different user groups. We offer a flexible way, json files to be specific, to config the settings.

## Quick Start

First, install the requirement packages declared by `requirements.txt`. 

Modify settings/example.json on your desired processing procedure. The configuration file may contains many options. For example, if you want to use regular expressions to match some dirty tokens, you should add your own regular expressions into `re_list` of `rm_re_rules`. Also, make sure value of `use` of its father components (i.e. `rm_re_rules` and `if_clean`) are `true`. Similar modifications for other settings.

Copy raw data to input_path in settings/example.json. And make sure the output_path not exists, otherwise the output path will be covered by temporary and output files.

```{commandline}
pip install -r requirements.txt
cp <raw_data> /path/to/input_path
mkdir /path/to/output_path
python main.py --conf settings/example.json
```

Then the processing pipeline will generate an `debug_report.json` into /path/to/report_path defined in `settings/example.json`. The report displayed filter ratio of each filter rules, as well as match ratio, time cost and match cases of each regular expression cleaner rules and so on.

After running the processing pipeline, the cleaned data will be merged as a `.jsonl` file, while there is just one record in a line. The record is in the form of `json`, with two keys `text` and `source`, representing processed text and source of raw data accordingly.

## Basic Components

The basic components of ZHEM pipeline are illustrated as follows.

![Basic components of ZHEM pipeline](assets/ZHEM.png)

### Loading Configuration Settings

### Rearranger 

### Debugger

### Extractor

### Filter

### Cleaner

### Deduplicator