import logging

import colorlog
import pytest
from rich import print as rprint

from wujing.llm.llm_call import llm_call


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    handler = colorlog.StreamHandler()
    handler.setFormatter(
        colorlog.ColoredFormatter(
            "%(log_color)s%(levelname)s:%(name)s:%(message)s",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
        )
    )
    logger.addHandler(handler)


def test_llm_call_with_openai_prompt(volces, messages, response_model):
    resp = llm_call(
        api_key=volces[1],
        api_base=volces[0],
        model=volces[2],
        messages=messages,
        protocol="openai",
        cache_enabled=False,
    )
    rprint(f"{resp=}")

    resp_with_response_model = llm_call(
        api_key=volces[1],
        api_base=volces[0],
        model=volces[2],
        messages=messages,
        response_model=response_model,
        protocol="openai",
        formatter="prompt",
        cache_enabled=False,
    )
    rprint(f"{response_model.model_validate_json(resp_with_response_model)=}")


def test_llm_call_with_openai_vllm(vllm, messages, response_model, context):
    resp = llm_call(
        api_key=vllm[1],
        api_base=vllm[0],
        model=vllm[2],
        messages=messages,
        protocol="openai",
        cache_enabled=False,
    )
    rprint(f"{resp=}")

    resp_with_response_model = llm_call(
        api_key=vllm[1],
        api_base=vllm[0],
        model=vllm[2],
        messages=messages,
        response_model=response_model,
        context=context,
        protocol="openai",
        formatter="vllm",
        cache_enabled=False,
    )
    rprint(f"{response_model.model_validate_json(resp_with_response_model)=}")


def test_llm_call_with_openai_vllm_v2(vllm, messages, response_model_with_root_model, context):
    resp = llm_call(
        api_key=vllm[1],
        api_base=vllm[0],
        model=vllm[2],
        messages=messages,
        protocol="openai",
        cache_enabled=False,
    )
    rprint(f"{resp=}")

    resp_with_response_model = llm_call(
        api_key=vllm[1],
        api_base=vllm[0],
        model=vllm[2],
        messages=messages,
        response_model=response_model_with_root_model,
        context=context,
        protocol="openai",
        formatter="vllm",
        cache_enabled=False,
    )
    rprint(f"{response_model_with_root_model.model_validate_json(resp_with_response_model)=}")


def test_llm_call_with_azure(azure, messages, response_model):
    resp = llm_call(
        api_key=azure[1],
        api_version=azure[2],
        api_base=azure[0],
        model=azure[3],
        messages=messages,
        protocol="azure",
        cache_enabled=False,
    )
    rprint(f"{resp=}")

    resp_with_response_model = llm_call(
        api_key=azure[1],
        api_version=azure[2],
        api_base=azure[0],
        model=azure[3],
        messages=messages,
        response_model=response_model,
        protocol="azure",
        formatter="azure",
        cache_enabled=False,
    )
    rprint(f"{response_model.model_validate_json(resp_with_response_model)=}")


def test_llm_call_formatter_mismatch_raises_exception(volces, messages, response_model):
    common_params = {
        "api_key": volces[1],
        "api_base": volces[0],
        "model": volces[2],
        "messages": messages,
        "protocol": "openai",
        "cache_enabled": False,
    }

    v1_rst = llm_call(
        **common_params,
        response_model=response_model,
        formatter="prompt",
    )
    assert v1_rst is not None
    assert response_model.model_validate_json(v1_rst) is not None

    with pytest.raises(Exception):
        llm_call(
            **common_params,
            response_model=response_model,
            formatter="vllm",
        )
