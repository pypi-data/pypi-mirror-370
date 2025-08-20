from pydantic import BaseModel, Field
from typing import List, Tuple
from ..src.quickbot_agent.utils import generate_gpt_tool_schema

META_SCHEMA_REQUIRED_KEYS = {"name", "description", "parameters"}


def test_simple_model():
    class SimpleModel(BaseModel):
        a: int = Field(..., description="A")
        b: str = Field("x", description="B")

    schema = generate_gpt_tool_schema(
        func=None, name="simple", description="desc", param_model=SimpleModel
    )
    assert set(schema.keys()) == META_SCHEMA_REQUIRED_KEYS
    assert "type" not in schema
    assert schema["parameters"]["type"] == "object"
    assert "a" in schema["parameters"]["properties"]
    assert "b" in schema["parameters"]["properties"]
    assert "a" in schema["parameters"]["required"]
    assert "b" not in schema["parameters"].get("required", [])
    assert schema["parameters"]["properties"]["a"]["type"] == "number"
    assert schema["parameters"]["properties"]["b"]["type"] == "string"
    assert schema["parameters"]["properties"]["a"]["description"] == "A"


def test_nested_model():
    class Inner(BaseModel):
        x: int = Field(...)

    class Outer(BaseModel):
        inner: Inner = Field(...)

    schema = generate_gpt_tool_schema(
        func=None, name="nested", description="desc", param_model=Outer
    )
    assert schema["parameters"]["properties"]["inner"]["type"] == "object"
    assert "x" in schema["parameters"]["properties"]["inner"]["properties"]
    assert schema["parameters"]["properties"]["inner"]["additionalProperties"] is False
    assert schema["parameters"]["additionalProperties"] is False


def test_list_3d():
    class List3D(BaseModel):
        matrix: List[List[List[int]]] = Field(...)

    schema = generate_gpt_tool_schema(
        func=None, name="list3d", description="desc", param_model=List3D
    )
    m = schema["parameters"]["properties"]["matrix"]
    assert m["type"] == "array"
    assert m["items"]["type"] == "array"
    assert m["items"]["items"]["type"] == "array"
    assert m["items"]["items"]["items"]["type"] == "number"


def test_tuple_prefix_items():
    class TupleModel(BaseModel):
        t: Tuple[str, int, bool] = Field(...)

    schema = generate_gpt_tool_schema(
        func=None, name="tuple", description="desc", param_model=TupleModel
    )
    t = schema["parameters"]["properties"]["t"]
    assert t["type"] == "array"
    assert "prefixItems" in t
    assert t["prefixItems"][0]["type"] == "string"
    assert t["prefixItems"][1]["type"] == "number"
    assert t["prefixItems"][2]["type"] == "boolean"


def test_required_with_defaults():
    class Model(BaseModel):
        a: int = Field(...)
        b: int = Field(5)
        c: int = Field(None)
        d: int = Field()

    schema = generate_gpt_tool_schema(
        func=None, name="req", description="desc", param_model=Model
    )
    req = schema["parameters"]["required"]
    assert "a" in req
    assert "d" in req
    assert "b" not in req
    assert "c" not in req


def test_no_type_function():
    class M(BaseModel):
        x: int

    schema = generate_gpt_tool_schema(
        func=None, name="m", description="desc", param_model=M
    )
    assert "type" not in schema
    assert set(schema.keys()) == META_SCHEMA_REQUIRED_KEYS
