from wujing.llm.retry import create_clean_model
from pydantic import BaseModel, Field, field_validator, ValidationError, RootModel, ConfigDict
import pytest


def test_clean_model():
    """测试创建干净模型的功能"""

    class intent_list(RootModel[list[str]]):
        root: list[str] = Field(description="List of column intents")

        model_config = ConfigDict(arbitrary_types_allowed=True)

    clean_model = create_clean_model(intent_list)
    print(intent_list.model_json_schema())
    print(clean_model.model_json_schema())

    assert isinstance(clean_model, type)


def test_create_clean_model():
    """测试创建干净模型的功能"""

    class TestModel(BaseModel):
        name: str
        age: int

    clean_model = create_clean_model(TestModel)

    assert isinstance(clean_model, type)


def test_create_clean_model_with_validators():
    """测试创建带验证器的干净模型"""

    class UserModel(BaseModel):
        name: str = Field(..., min_length=2, max_length=50)
        age: int = Field(..., ge=0, le=150)
        email: str

        @field_validator("email")
        @classmethod
        def validate_email(cls, v):
            if "@" not in v:
                raise ValueError("必须包含@符号")
            return v

        @field_validator("name")
        @classmethod
        def validate_name(cls, v):
            if not v.strip():
                raise ValueError("姓名不能为空")
            return v.strip()

    clean_model = create_clean_model(UserModel)

    with pytest.raises(ValidationError):
        UserModel(name="", age=25, email="invalid-email")

    clean_instance = clean_model(name="", age=25, email="invalid-email")
    assert clean_instance.name == ""
    assert clean_instance.age == 25
    assert clean_instance.email == "invalid-email"

    original_fields = UserModel.model_fields
    clean_fields = clean_model.model_fields

    assert set(original_fields.keys()) == set(clean_fields.keys())
    for field_name in original_fields:
        assert original_fields[field_name].annotation == clean_fields[field_name].annotation


def test_clean_model_preserves_root_description():
    """测试 RootModel 的描述信息是否被正确保留"""

    class DocumentList(RootModel[list[str]]):
        """文档列表模型"""

        root: list[str] = Field(description="包含所有文档标题的列表")

    clean_model = create_clean_model(DocumentList)

    # 检查原始模型的 schema
    original_schema = DocumentList.model_json_schema()
    clean_schema = clean_model.model_json_schema()

    print("原始模型 schema:", original_schema)
    print("清理后模型 schema:", clean_schema)

    # 验证结构保持一致（都是数组类型）
    assert original_schema["type"] == "array"
    assert clean_schema["type"] == "array"

    # 验证描述信息（原始的字段描述变成了模型描述）
    assert "description" in original_schema
    assert "description" in clean_schema

    # 验证数组项类型保持一致
    assert original_schema["items"] == clean_schema["items"]


def test_clean_model_preserves_basemodel_descriptions():
    """测试 BaseModel 的字段描述信息是否被正确保留"""

    class ProductInfo(BaseModel):
        """产品信息模型"""

        name: str = Field(description="产品名称")
        price: float = Field(description="产品价格", ge=0)
        description: str = Field(description="产品详细描述")

    clean_model = create_clean_model(ProductInfo)

    # 检查字段描述是否被保留
    original_fields = ProductInfo.model_fields
    clean_fields = clean_model.model_fields

    # 验证所有字段都存在
    assert set(original_fields.keys()) == set(clean_fields.keys())

    # 验证字段描述被保留
    for field_name in ["name", "price", "description"]:
        original_field = original_fields[field_name]
        clean_field = clean_fields[field_name]

        if original_field.description:
            # 如果原始字段有描述，清理后的字段也应该有相同的描述
            assert hasattr(clean_field, "description")
            assert clean_field.description == original_field.description

        # 验证类型注解保持一致
        assert original_field.annotation == clean_field.annotation
