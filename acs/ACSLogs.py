import logging
import os

class ACSLog:
    def __init__(self, name = "acs"):
        output_dir = 'logs'
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        if (not self.logger.handlers):
            # create console handler and set level to info
            handler = logging.StreamHandler()
            handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            
            # create error file handler and set level to error
            handler = logging.FileHandler(os.path.join(output_dir, "error.log"),"w", encoding=None, delay="true")
            handler.setLevel(logging.ERROR)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            
            # create debug file handler and set level to debug
            handler = logging.FileHandler(os.path.join(output_dir, "all.log"),"w")
            handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def info(self, msg):
        self.logger.info(msg)

    def debug(self, msg):
        self.logger.debug(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)
