from utils.workers import Extractor, Cleaner, Filter

class ModuleManager:
    def __init__(self):
        self.extract_module = Extractor()
        self.clean_module = Cleaner()
        self.filter_module = Filter()

    def load_modules(self, settings: dict):
        self.extract_module = Extractor(setting=settings)
        self.clean_module = Cleaner(setting=settings)
        self.filter_module = Filter(setting=settings)

modulemanager = ModuleManager()