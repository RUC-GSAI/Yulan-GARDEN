from collections import defaultdict
import json

class Settings:
    def __init__(
            self, 
    ):
        self.settings = defaultdict(str)
        self.conf_path = ""


    def load_settings(
            self, conf_path: str=""
    ) -> None:
        try:
            if conf_path == "":
                with open(self.conf_path, 'r') as fr:
                    self.settings = json.load(fr)
            else:
                with open(conf_path, 'r') as fr:
                    self.settings = json.load(fr)
        except Exception as ne:
            assert(f"[Error] Exception {ne} raised in settings.loader. Maybe the settings json file not exists!!")