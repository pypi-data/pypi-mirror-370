# LLM Inference, 开箱即用的本地 LLM 推理 SDK

## 安装

- pip

    ```
    pip install git+https://gitlab.changdu.ltd/060270/llm_inference.git@main
    ```

- uv

    ```
    uv add git+https://gitlab.changdu.ltd/060270/llm_inference.git@main
    ```

## 主要功能

1. ### Seed-X 机器翻译
    
    ```python
    from vllm_inference.translation.seed_x import translate
    ```

    ```python
    translation = translate('你好, 我叫吴子豪!', 'fr', max_tokens=2048, temperature=.0, top_p=.01)
    ```
    