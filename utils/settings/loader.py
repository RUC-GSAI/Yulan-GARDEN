from collections import defaultdict
import json

class Settings:
    def __init__(
            self, conf_path: str=""
    ):
        self.settings = defaultdict(str)
        self.load_settings(conf_path)

    def load_settings(
            self, conf_path: str=""
    ) -> None:
        try:
            with open(conf_path, 'r') as fr:
                self.settings = json.load(fr)
        except Exception as ne:
            assert(f"[Error] Exception {ne} raised in settings.loader. Maybe the settings json file not exists!!")