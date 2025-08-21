import logging

import colorlog
from openai import OpenAI


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


def test_with_vllm(vllm, messages, response_model):
    setup_logging()

    client = OpenAI(
        api_key=vllm[1],
        base_url=vllm[0],
    )

    resp = client.beta.chat.completions.parse(
        model="Qwen3-235B-A22B-Instruct-2507",
        response_format=response_model,
        messages=messages,
    )

    logging.info(f": {resp=}")