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
                self.settings = json.loads(self.conf_path)
            else:
                self.settings = json.loads(conf_path)
        except Exception as ne:
            assert(f"[Error] Exception {ne} raised in settings.loader. Maybe the settings json file not exists!!")