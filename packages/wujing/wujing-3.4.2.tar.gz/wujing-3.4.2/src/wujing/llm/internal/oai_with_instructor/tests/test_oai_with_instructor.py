from rich import print as rprint

from wujing.llm.internal.oai_with_instructor.oai_with_instructor import oai_with_instructor


def test_oai_call(volces, messages, response_model):
    resp = oai_with_instructor(
        api_key=volces[1],
        api_base=volces[0],
        model=volces[2],
        messages=messages,
        response_model=response_model,
    )

    rprint(f"{type(resp)=}, {resp=}")
