import logging

class Logger():
    def __init__(self, name="Global Logger", file="tmp/process.log"):
        self.logger = logging.getLogger(name)

        if file:
            file_handler = logging.FileHandler(file)
            self.logger.addHandler(file_handler)
        
        self.logger.setLevel(logging.INFO)
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def log_text(self, text: str, desc: str="info"):        
        if desc.lower() == 'info':
            self.logger.info(text)
        elif desc.lower() == 'debug':
            self.logger.debug(text)
        elif desc.lower() == 'warning':
            self.logger.warning(text)
        elif desc.lower() == 'error':
            self.logger.error(text)
        elif desc.lower() == 'critical':
            self.logger.error(text)
        else:
            raise Exception(f"illegal mode {desc} in func log_text()...")

        
global_logger = Logger(
    name = "Global Logger"
)