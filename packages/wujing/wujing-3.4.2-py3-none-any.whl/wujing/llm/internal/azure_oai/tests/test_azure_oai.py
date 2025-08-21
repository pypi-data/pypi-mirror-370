from rich import print as rprint

from wujing.llm.internal.azure_oai.azure_oai import azure_oai


def test_azure_oai(azure, messages, response_model):
    resp = azure_oai(
        azure_endpoint=azure[0],
        api_key=azure[1],
        api_version=azure[2],
        model=azure[3],
        messages=messages,
    )

    rprint(f"{type(resp)=}, {resp=}")


def test_azure_oai_with_response_model(azure, messages, response_model):
    resp = azure_oai(
        azure_endpoint=azure[0],
        api_key=azure[1],
        api_version=azure[2],
        model=azure[3],
        messages=messages,
        response_model=response_model,
    )

    assert response_model.model_validate_json(resp) is not None

    rprint(f"{type(resp)=}, {resp=}")
