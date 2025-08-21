import logging

from vllm import LLM, TextPrompt
from vllm.model_executor.guided_decoding.guided_fields import GuidedDecodingRequest
from vllm.sampling_params import BeamSearchParams, SamplingParams

logger = logging.getLogger('vllm_inference')


def inference_with_beam_search(prompt: str, llm: LLM, temperature: float = .0, beam_width: int = 4, max_tokens: int = 4096) -> list[tuple[str, float]]:
    beam_search_params = BeamSearchParams(temperature=temperature, beam_width=beam_width, max_tokens=max_tokens, include_stop_str_in_output=False)
    results = llm.beam_search(prompts=[TextPrompt(prompt=prompt)], params=beam_search_params)[0].sequences
    results.sort(key=lambda x: x.cum_logprob, reverse=True)
    logger.debug(f'inference_with_beam_search: {results}')
    return [(res.text, res.cum_logprob) for res in results]


def inference(prompt: str | list[str], llm: LLM, regex: str | None = None, **kwargs) -> list[str]:
    prompt = [TextPrompt(prompt=prompt)] if isinstance(prompt, str) else [TextPrompt(prompt=p) for p in prompt]
    max_retry = 8
    retry = 0
    tmp_results = []
    results = []
    while retry < max_retry:
        results = llm.generate(prompt, sampling_params=SamplingParams(**kwargs),
                               guided_options_request=GuidedDecodingRequest(guided_regex=regex) if regex else None,
                               use_tqdm=True)
        logger.debug(f'inference: {results}')
        tmp_results.extend(results)
        results = [y.text for y in [x.outputs[0] for x in results] if y.finish_reason.lower() == 'stop']
        if len(results) > 0:
            return results
        retry += 1
    return results if len(results) else tmp_results
