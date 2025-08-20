import logging
import os

__ROOT__ = os.path.dirname(__file__)
os.environ['HF_HOME'] = os.path.join(__ROOT__, '.cache')
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

logger = logging.getLogger('vllm_inference')
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('[%(levelname)s] %(asctime)s %(name)s : %(message)s')

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
