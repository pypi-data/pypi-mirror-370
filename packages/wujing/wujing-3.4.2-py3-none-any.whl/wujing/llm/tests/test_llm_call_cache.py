from time import perf_counter
from typing import Type

from pydantic import BaseModel, validate_call

from wujing.llm.llm_call import llm_call
from wujing.llm.types import ResponseModelType

query = """
你是一个数据分析专家，给你一份用户的数据, 请你对数据理解并根据下面的要求响应用户，
目前数据在 DuckDB 表中，
一部分采样数据如下:
    序号       车次   始发站  终到站        到点        开点             候车厅 检票口   站台
0  2.0     Z362  乌鲁木齐   南通  00:10:00  00:21:00  综合候乘中心，高架候车区西区  5B  5.0
1  5.0     K178    西宁   郑州  00:48:00  01:02:00  综合候乘中心，高架候车区西区  8B  2.0
2  3.0     T308  乌鲁木齐   南昌  00:16:00  00:28:00  综合候乘中心，高架候车区西区  1A  5.0
3  1.0  K4547/6   成都西  佳木斯  23:40:00  00:12:00  综合候乘中心，高架候车区西区  1B  2.0
4  4.0     D218    兰州   上海  00:42:00  00:53:00  综合候乘中心，高架候车区西区  2A  1.0

DuckDB 表结构信息如下：

CREATE TABLE xiantieluju_csv (
	"序号" FLOAT, 
	"车次" VARCHAR, 
	"始发站" VARCHAR, 
	"终到站" VARCHAR, 
	"到点" TIME WITHOUT TIME ZONE, 
	"开点" TIME WITHOUT TIME ZONE, 
	"候车厅" VARCHAR, 
	"检票口" VARCHAR, 
	"站台" FLOAT
)




分析各列数据的含义和作用，并对专业术语进行简单明了的解释, 具体要求：
1. 仔细阅读给你的表结构、数据样例
2. 提取出字段的列名、数据类型、数据含义、数据格式等信息
3. 概述数据内容，给出数据分析总结

请一步一步思考,确保只以JSON格式回答，并且需要能被 Python 的 json.loads() 函数解析。
响应格式如下:
```json
{
    "data_summary": "数据内容分析概要",
}
```
""".strip()


class Table_Summary(BaseModel):
    data_summary: str


@validate_call(config=dict(arbitrary_types_allowed=True, validate_assignment=False))
def send_req(
    *,
    query: str,
    api_key: str,
    api_base: str,
    model: str,
    response_model: Type[ResponseModelType],
    context: dict = None,
    cache_enable: bool = True,
    formatter: str = "prompt",
) -> ResponseModelType:
    rst = llm_call(
        api_key=api_key,
        api_base=api_base,
        model=model,
        messages=[
            {"role": "user", "content": query},
        ],
        response_model=response_model,
        formatter=formatter,
        cache_enabled=cache_enable,
        cache_directory="/root/.diskcache/llm_cache",
        context=context,
    )
    return response_model.model_validate_json(rst)


def test_llm_call_cache(volces):
    start_time = perf_counter()
    send_req(
        query=query,
        api_key=volces[1],
        api_base=volces[0],
        model=volces[2],
        response_model=Table_Summary,
    )
    first_call_elapsed = perf_counter() - start_time

    start_time = perf_counter()
    send_req(
        query=query,
        api_key=volces[1],
        api_base=volces[0],
        model=volces[2],
        response_model=Table_Summary,
    )
    second_call_elapsed = perf_counter() - start_time

    assert second_call_elapsed < first_call_elapsed, (
        f"缓存未命中，第二次调用时间: {second_call_elapsed:.4f}s vs 第一次调用时间: {first_call_elapsed:.4f}s"
    )
    assert second_call_elapsed < 1.0, f"缓存命中时间过长，第二次调用时间: {second_call_elapsed:.4f}s"
