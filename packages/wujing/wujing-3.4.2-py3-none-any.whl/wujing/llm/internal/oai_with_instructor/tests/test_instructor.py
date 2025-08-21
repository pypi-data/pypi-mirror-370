import logging

import colorlog
import instructor
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


def test_with_vllm(volces, messages, response_model, context):
    setup_logging()

    client = instructor.from_openai(
        client=OpenAI(api_key=volces[1], base_url=volces[0]),
        mode=instructor.Mode.JSON,
    )

    logging.info("开始测试 volces 集成")
    logging.debug("volces 配置: %s", volces)

    try:
        user = client.chat.completions.create(
            model=volces[2],
            response_model=response_model,
            messages=messages,
            context=context,
        )
    except Exception as e:
        logging.error(f"vllm 测试失败: {type(e)=},{e=}")
        raise

    logging.info(f"用户详情: {user=}")
    logging.debug("测试完成")
