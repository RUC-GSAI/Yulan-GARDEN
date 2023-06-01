# ZHEM

## Introduction

ZHEM is a Chinese(ZH-*, like zh-cn, zh-tw and so on) Natural Language data Cleaning Pipeline for training Large Language Models(LLMs) developed by [@Emanual20](https://github.com/Emanual20). 

The target datasets of this pipeline are mainly larger than 100GB. The pipeline cost will be prohibitively long when only single thread is used. As a result, we introduced multi-processing to this pipeline.

Since the nodes for processing data and the desired filtering/cleaning power may vary to a large extent among different user groups. We offer a flexible way, json files, to config the settings. To simplify the process, you could also use default configuration by command lines.

## Quick Start

## Basic Components