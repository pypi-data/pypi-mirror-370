from rich.pretty import pretty_repr

from wujing.llm.extract import extract_code

sample_markdown1 = """
# Markdown 代码提取示例

这是一个介绍性段落。下面是第一个代码块，它是一个 SQL 查询。

```sql
SELECT
车次,
终到站,
席位
FROM
data
WHERE
起始站 = '兰州' AND 终到站 = '北京西';
````

接下来，让我们看一个 Python 函数的例子。

```python
def calculate_sum(a, b):
# 这是一个简单的求和函数
return a + b
```

这是一个没有语言标识符的代码块：

```
echo "Hello World!"
```

最后一段文本。
"""

sample_markdown2 = """
echo "Hello World!"
"""


def test_extract_code():
    print(f"{pretty_repr(extract_code(sample_markdown1))=}")
    print(f"{pretty_repr(extract_code(sample_markdown2))=}")
