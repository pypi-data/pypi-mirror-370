import logging

from vllm import LLM
from vllm.model_executor.layers.quantization import QuantizationMethods
from vllm_inference.inference import inference

logger = logging.getLogger('vllm_inference')


def load_model(model_name: str = 'ByteDance-Seed/Seed-X-PPO-7B-GPTQ-Int8', gpu_memory_utilization: float = .9,
               swap_space: float = 0, cpu_offload_gb: float = 0, max_seq_len_to_capture: int = 4096,
               quantization: QuantizationMethods = 'fp8'):
    return LLM(model=model_name, trust_remote_code=True, gpu_memory_utilization=gpu_memory_utilization,
               swap_space=swap_space, cpu_offload_gb=cpu_offload_gb, max_seq_len_to_capture=max_seq_len_to_capture,
               quantization=quantization)


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
