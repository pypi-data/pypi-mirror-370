import mistune


class CodeExtractorRenderer(mistune.HTMLRenderer):
    def __init__(self):
        super().__init__()
        self.extracted_codes = []  # 用于存储所有找到的代码块

    def block_code(self, code: str, info: str = None) -> str:
        """
        当 mistune 解析器遇到一个代码块时，会调用这个方法。

        Args:
            code: 实际的源代码内容。
            info: 语言标识符 (如 'python', 'sql' 等)。

        Returns:
            我们不关心渲染结果，所以返回空字符串。
        """
        self.extracted_codes.append(code)
        return ""


def extract_code(markdown_text: str) -> list[str]:
    """
    使用 mistune 库从 Markdown 文本中提取所有代码块。

    Args:
        markdown_text: 包含 Markdown 格式的字符串。

    Returns:
        一个包含所有提取出的源代码字符串的列表。
    """
    code_extractor_renderer = CodeExtractorRenderer()
    markdown_parser = mistune.create_markdown(renderer=code_extractor_renderer)
    markdown_parser(markdown_text)
    return code_extractor_renderer.extracted_codes
