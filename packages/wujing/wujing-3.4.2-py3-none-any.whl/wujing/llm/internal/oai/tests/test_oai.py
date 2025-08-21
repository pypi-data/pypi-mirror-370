from rich import print as rprint

from wujing.llm.internal.oai.oai import oai


def test_oai_call(volces, messages):
    resp = oai(
        api_key=volces[1],
        api_base=volces[0],
        model=volces[2],
        messages=messages,
    )

    rprint(f"{type(resp)=}, {resp=}")
