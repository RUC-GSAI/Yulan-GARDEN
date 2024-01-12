from utils.settings import *

import json
from bs4 import BeautifulSoup

class Extractor:
    def __init__(self, setting: Settings=None) -> None:
        self.extract_setting = {}
        
        if setting:
            self.load_settings(setting=setting)

    def load_settings(self, setting: Settings) -> None:
        self.extract_setting = setting['clean_paras']['extractor']
        self.if_extract = self.extract_setting['use']
        # loading extractor mode
        self.mode = ""
        for each in self.extract_setting['mode'].keys():
            self.mode = each if self.extract_setting['mode'][each] else self.mode
        # todo
        self.keep_newline_labels = self.extract_setting['keep_newline_labels']

    def extract(self, text: str) -> str:
        '''
        Params: raw data text, maybe containing html labels, maybe in format of epub/mobi
        Ret: a piece of extracted text
        '''
        if self.if_extract:
            try:
                if self.mode == "html":
                    text = BeautifulSoup(text, features='html.parser').get_text(separator="\n", strip=True)
                    text = text.strip()
                    return text
                elif self.mode == "epub":                    
                    return text
                elif self.mode == "mobi":
                    return text
                elif self.mode == "":
                    return text
                else:
                    raise Exception(f"Not valid mode name {self.mode}")
            except:
                return ""
        else:
            return text