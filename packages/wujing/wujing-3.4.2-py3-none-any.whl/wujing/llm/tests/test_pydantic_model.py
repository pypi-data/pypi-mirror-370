from pydantic import BaseModel, ValidationError, field_validator
from rich import print as rprint


class Model(BaseModel):
    content: str

    @field_validator("content")
    def validate_content(cls, v):
        if v == "trigger_value_error":
            raise ValueError("内容不能是 'trigger_value_error'")
        if v == "trigger_type_error":
            raise TypeError("内容类型错误")
        return v


def test_validation_errors():
    test_cases = [
        ({"content": "trigger_value_error"}, "触发自定义 ValueError"),
        ({"content": "trigger_type_error"}, "触发自定义 TypeError"),
    ]

    for test_data, description in test_cases:
        rprint(f"\n[blue]测试: {description}[/blue]")
        try:
            result = Model.model_validate(test_data)
            rprint(f"[green]意外成功: {result}[/green]")
        except ValidationError as e:
            rprint(f"[yellow]预期的验证错误: {e.error_count()} 个错误[/yellow]")
            for error in e.errors():
                rprint(f"  - {error['loc']}: {error['msg']} ({error['type']})")
        except ValueError as e:
            rprint(f"[orange]值错误: {e}[/orange]")
        except TypeError as e:
            rprint(f"[red]类型错误: {e}[/red]")
        except Exception as e:
            rprint(f"[red]未预期的错误: {type(e).__name__} - {e}[/red]")
