import logging

from vllm import LLM
from vllm_inference.inference import inference

logger = logging.getLogger('vllm_inference')


def translate_cot(llm: LLM, sentence: str, prefix: str = '', target_lang: str = 'en', resample: int = 1, **kwargs) -> str:
    pre_think = '[COT]'
    post_think = '[COT]'
    lang_seq = f'<{target_lang.lower().replace("<", "").replace(">", "")}>'
    kwargs['stop'] = post_think
    prompt = f'Translate the sentence and explain in detail.<sentence>{sentence}</sentence>{lang_seq}{pre_think}{prefix}'
    logger.debug(f'PROMPT: {prompt.replace("\n", " ")}')
    cot = sorted(inference(prompt=[prompt] * resample, llm=llm, **kwargs),
                 key=lambda x: len(x[0]), reverse=True)[0]
    logger.debug(f'COT: {cot}')
    return cot
