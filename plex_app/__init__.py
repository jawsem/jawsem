import os
import sys
import logging

log_file = 'base_app.log'
logging.basicConfig(level=logging.DEBUG,
                            format="%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s",
                            filename=log_file)
dirname=os.path.dirname(os.abspath(__file__))
sys.path.append(dirname)
