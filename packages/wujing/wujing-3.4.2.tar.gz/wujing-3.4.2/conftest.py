import pytest
from pydantic import BaseModel, RootModel


@pytest.fixture(autouse=True)
def separator(request):
    test_name = request.node.name
    print(f"\n{'>' * 30} START: {test_name} {'<' * 30}")
    yield


@pytest.fixture(scope="session")
def volces():
    return ("https://ark.cn-beijing.volces.com/api/v3", "3a6615d7-fbfa-4a5e-a675-ad2f43d8985f", "deepseek-v3-250324")


@pytest.fixture(scope="session")
def vllm():
    return ("http://127.0.0.1:8002/v1", "sk-xylx1.t!@#", "Qwen3-235B-A22B-Instruct-2507")


@pytest.fixture(scope="session")
def azure():
    return (
        "https://gpt5-rdg.openai.azure.com",
        "AV4Pl6XZbGOJMgt9q866JBJKUnYTE6UARYCQl5NVERyX1UyeAgLCJQQJ99BHACHYHv6XJ3w3AAABACOGwc61",
        "2025-04-01-preview",
        "gpt-5",
    )


@pytest.fixture(scope="session")
def model():
    return "deepseek-v3-250324"


@pytest.fixture(scope="session")
def messages():
    return [
        {
            "role": "user",
            "content": "Hello, how are you?",
        },
    ]


@pytest.fixture(scope="session")
def context():
    return {"test": "this is a test context", "info": "additional information for testing"}


class ResponseModel(BaseModel):
    content: str


@pytest.fixture(scope="session", params=[ResponseModel])
def response_model(request):
    return request.param


class ResponseModelWithRootModel(RootModel[list[str]]):
    pass


@pytest.fixture(scope="session", params=[ResponseModelWithRootModel])
def response_model_with_root_model(request):
    return request.param
