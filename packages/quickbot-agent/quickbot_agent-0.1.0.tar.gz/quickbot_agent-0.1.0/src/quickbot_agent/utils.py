# Полный код: генерация схемы GPT-инструмента на основе Pydantic-модели и Python-функции

from datetime import datetime, date, time
from decimal import Decimal
from typing import (
    get_args,
    get_origin,
    Union,
    List,
    Dict,
    Tuple,
)
from sqlmodel import select, col
from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic import BaseModel
import sys

from quickbot.model.bot_entity import BotEntity
from quickbot.model.crud_command import CrudCommand
from quickbot.model.bot_metadata import BotMetadata
from quickbot.model.descriptors import EntityDescriptor
from quickbot.model.bot_process import BotProcess
from quickbot.model.user import UserBase

from .model import MessageLog
from .config import config


# Рекурсивное определение JSON Schema по типу
def resolve_json_schema_type(py_type: type) -> dict:
    origin = get_origin(py_type)
    args = get_args(py_type)

    if py_type in (str, datetime, date, time, int, float, Decimal, bool):
        return {"type": type_name(py_type)}
    elif py_type is None or py_type is type(None):
        return {"type": "null"}

    if origin is Union and type(None) in args:
        non_null = [arg for arg in args if arg is not type(None)]
        if len(non_null) == 1:
            schema = resolve_json_schema_type(non_null[0])
            schema["type"] = [schema["type"], "null"]
            return schema
        else:
            return {
                "anyOf": [resolve_json_schema_type(arg) for arg in non_null]
                + [{"type": "null"}]
            }

    if origin in (list, List):
        item_schema = resolve_json_schema_type(args[0]) if args else {}
        return {"type": "array", "items": item_schema}

    if origin in (dict, Dict):
        key_type, value_type = args if args else (str, object)
        if key_type not in (str,):
            raise ValueError("JSON object keys must be strings")
        return {
            "type": "object",
            "additionalProperties": resolve_json_schema_type(value_type),
        }

    if origin in (tuple, Tuple) and args:
        if len(args) == 2 and args[1] is Ellipsis:
            return {"type": "array", "items": resolve_json_schema_type(args[0])}
        return {
            "type": "array",
            "prefixItems": [resolve_json_schema_type(arg) for arg in args],
        }

    if sys.version_info >= (3, 8):
        from typing import Literal

        if origin is Literal:
            literals = list(args)
            literal_type = type(literals[0]) if literals else "string"
            return {"type": type_name(literal_type), "enum": literals}

    if isinstance(py_type, type) and issubclass(py_type, BaseModel):
        return generate_parameters_from_pydantic(py_type)

    return {"type": "string"}


def type_name(t: type) -> str:
    if t in (str, datetime, date, time):
        return "string"
    elif t in (int, float, Decimal):
        return "number"
    elif t in (bool,):
        return "boolean"
    elif t in (list, List):
        return "array"
    elif t in (dict, Dict):
        return "object"
    else:
        return "string"


def add_additional_properties_false(schema: dict):
    """
    Рекурсивно добавляет additionalProperties: False для всех объектов в схеме.
    """
    if schema.get("type") == "object":
        schema["additionalProperties"] = False
        for prop in schema.get("properties", {}).values():
            add_additional_properties_false(prop)
    elif schema.get("type") == "array" and "items" in schema:
        if isinstance(schema["items"], dict):
            add_additional_properties_false(schema["items"])
        elif isinstance(schema["items"], list):
            for item in schema["items"]:
                add_additional_properties_false(item)
    if "anyOf" in schema:
        for sub in schema["anyOf"]:
            add_additional_properties_false(sub)
    if "prefixItems" in schema:
        for sub in schema["prefixItems"]:
            add_additional_properties_false(sub)


# Генерация параметров по Pydantic-модели
# (добавляем additionalProperties: False для объектов)
def generate_parameters_from_pydantic(
    model: type[BaseModel], add_id: bool = False
) -> dict:
    schema = {
        "type": "object",
        "properties": {},
    }
    required = []
    for name, field in model.model_fields.items():
        field_schema = resolve_json_schema_type(field.annotation)
        if field.description:
            field_schema["description"] = field.description
        schema["properties"][name] = field_schema
        if field.is_required():
            required.append(name)
    if add_id:
        schema["properties"]["id"] = {
            "type": "number",
            "description": "ID of the entity",
        }
        if "id" not in required:
            required.append("id")
    if required:
        schema["required"] = required
    add_additional_properties_false(schema)
    return schema


# Основная функция генерации GPT-инструмента (строго по META_SCHEMA)
def generate_gpt_tool_schema(
    name: str,
    description: str,
    param_model: type[BaseModel] | None = None,
    add_id: bool = False,
) -> dict:
    parameters_schema = (
        generate_parameters_from_pydantic(param_model, add_id) if param_model else None
    )
    tool_schema = {
        "name": name,
        "description": description,
    }
    if parameters_schema:
        tool_schema["parameters"] = parameters_schema
    return {
        "type": "function",
        "function": tool_schema,
    }


def generate_crud_tool_schemas(
    entity_descriptor: EntityDescriptor,
    commands: list[CrudCommand] = [
        CrudCommand.LIST,
        CrudCommand.GET_BY_ID,
        CrudCommand.CREATE,
        CrudCommand.UPDATE,
        CrudCommand.DELETE,
    ],
) -> list[dict]:
    crud_tools = []

    if (
        CrudCommand.LIST in entity_descriptor.crud.commands
        and CrudCommand.LIST in commands
    ):
        tool = generate_gpt_tool_schema(
            name=f"model__{entity_descriptor.name}__{CrudCommand.LIST}",
            description=f"List all {entity_descriptor.name}s",
            param_model=None,
        )
        crud_tools.append(tool)

    # tool = FunctionToolParam(
    #     type="function",
    #     name=f"model_{entity_descriptor.name}_get_by_id",
    #     description=f"Get a {entity_descriptor.name} by ID",
    #     parameters=generate_parameters_from_pydantic(entity_descriptor.get_by_id_schema_class),
    # )

    if (
        CrudCommand.GET_BY_ID in entity_descriptor.crud.commands
        and CrudCommand.GET_BY_ID in commands
    ):
        tool = {
            "type": "function",
            "function": {
                "name": f"model__{entity_descriptor.name}__{CrudCommand.GET_BY_ID}",
                "description": f"Get a {entity_descriptor.name} by ID",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "number",
                            "description": "ID of the entity",
                        },
                    },
                },
            },
        }
        crud_tools.append(tool)

    if (
        CrudCommand.CREATE in entity_descriptor.crud.commands
        and CrudCommand.CREATE in commands
    ):
        tool = generate_gpt_tool_schema(
            name=f"model__{entity_descriptor.name}__{CrudCommand.CREATE}",
            description=f"Create a new {entity_descriptor.name}",
            param_model=entity_descriptor.crud.create_schema,
        )
        crud_tools.append(tool)

    if (
        CrudCommand.UPDATE in entity_descriptor.crud.commands
        and CrudCommand.UPDATE in commands
    ):
        tool = generate_gpt_tool_schema(
            name=f"model__{entity_descriptor.name}__{CrudCommand.UPDATE}",
            description=f"Update a {entity_descriptor.name} by ID",
            param_model=entity_descriptor.crud.update_schema,
            add_id=True,
        )
        crud_tools.append(tool)

    if (
        CrudCommand.DELETE in entity_descriptor.crud.commands
        and CrudCommand.DELETE in commands
    ):
        tool = {
            "type": "function",
            "function": {
                "name": f"model__{entity_descriptor.name}__{CrudCommand.DELETE}",
                "description": f"Delete a {entity_descriptor.name} by ID",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "number",
                            "description": "ID of the entity",
                        },
                    },
                },
            },
        }
        crud_tools.append(tool)

    return crud_tools


def generate_gpt_tools_schemas(
    metadata: BotMetadata,
    tools_context: list[
        type[BotEntity] | type[BotProcess] | tuple[BotEntity, list[CrudCommand]]
    ]
    | None = None,
) -> list[dict]:
    gpt_tools_schemas = []
    if tools_context is None:
        for entity_descriptor in metadata.entity_descriptors.values():
            gpt_tools_schemas.extend(generate_crud_tool_schemas(entity_descriptor))
    else:
        for tool_item in tools_context:
            if isinstance(tool_item, type) and issubclass(tool_item, BotProcess):
                gpt_tools_schemas.append(
                    generate_gpt_tool_schema(
                        name=f"process__{tool_item.bot_process_descriptor.name}",
                        description=tool_item.bot_process_descriptor.description,
                        param_model=tool_item.bot_process_descriptor.input_schema,
                    )
                )
            if isinstance(tool_item, type) and hasattr(
                tool_item, "bot_entity_descriptor"
            ):
                gpt_tools_schemas.extend(
                    generate_crud_tool_schemas(tool_item.bot_entity_descriptor)
                )
            elif isinstance(tool_item, tuple):
                entity, commands = tool_item
                if commands:
                    gpt_tools_schemas.extend(
                        generate_crud_tool_schemas(
                            entity.bot_entity_descriptor, commands=commands
                        )
                    )
                else:
                    gpt_tools_schemas.extend(
                        generate_crud_tool_schemas(entity.bot_entity_descriptor)
                    )
    return gpt_tools_schemas


async def get_message_log(
    db_session: AsyncSession, user: UserBase, client_id: int | None = None
):
    query = select(MessageLog).where(
        MessageLog.user_id == user.id,
    )
    if client_id:
        query = query.where(MessageLog.client_id == client_id)
    query = query.order_by(col(MessageLog.dt).desc()).limit(
        config.MESSAGE_HISTORY_DEPTH
    )
    result = await db_session.exec(query)
    return reversed(result.all())


async def add_message_log(
    db_session: AsyncSession,
    user: UserBase,
    client_id: int | None = None,
    content: str | None = None,
):
    message_log = MessageLog(
        user_id=user.id,
        is_business_chat=client_id is not None,
        client_id=client_id,
        content=content,
    )
    db_session.add(message_log)
    await db_session.commit()
