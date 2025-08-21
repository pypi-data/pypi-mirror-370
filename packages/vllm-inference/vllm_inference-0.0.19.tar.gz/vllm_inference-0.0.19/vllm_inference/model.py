from vllm import LLM
from vllm.model_executor.layers.quantization import QuantizationMethods


def load_model(model_name: str, gpu_memory_utilization: float = .9,
               swap_space: float = 0, cpu_offload_gb: float = 0, max_seq_len_to_capture: int = 4096,
               quantization: QuantizationMethods = 'fp8', **kwargs):
    return LLM(model=model_name, trust_remote_code=True, gpu_memory_utilization=gpu_memory_utilization,
               swap_space=swap_space, cpu_offload_gb=cpu_offload_gb, max_seq_len_to_capture=max_seq_len_to_capture,
               quantization=quantization, **kwargs)
