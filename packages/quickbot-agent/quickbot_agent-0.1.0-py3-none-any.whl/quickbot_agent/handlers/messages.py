from inspect import iscoroutinefunction
from aiogram import Router
from aiogram.types import Message
from aiogram.utils.i18n.lazy_proxy import LazyProxy
from fastapi.datastructures import State
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessage
from pydantic import BaseModel
from quickbot.model.user import UserBase
from sqlmodel.ext.asyncio.session import AsyncSession
from quickbot import QuickBot, BotContext
from quickbot.model.crud_service import ForbiddenError, NotFoundError
from quickbot.model.crud_command import CrudCommand
from ..utils import get_message_log, add_message_log, generate_gpt_tools_schemas
from typing import TYPE_CHECKING
import ujson as json
from ..config import config
from logging import getLogger

if TYPE_CHECKING:
    from ..main import AgentPlugin

logger = getLogger(__name__)

router = Router()


async def handle_openai_text(context: BotContext, output: ChatCompletionMessage):
    if output.content:
        await context.message.answer(output.content)
        await add_message_log(
            db_session=context.db_session,
            user=context.user,
            client_id=context.message.chat.id
            if context.message.business_connection_id
            else None,
            content=json.dumps(
                {"role": "assistant", "content": output.content}, ensure_ascii=False
            ),
        )


async def handle_openai_cycle(
    context: BotContext,
    client: AsyncOpenAI,
    plugin: "AgentPlugin",
    messages: list[dict],
):
    max_iterations = 10  # Prevent infinite loops
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        # response = await client.responses.create(
        #     background=False,
        #     instructions=system_prompt,
        #     input=messages,
        #     tools=plugin.gpt_tools_metadata,
        #     tool_choice="auto",
        #     model=config.OPENAI_MODEL,
        # )

        if callable(plugin.tools_context):
            if iscoroutinefunction(plugin.tools_context):
                tools_context = await plugin.tools_context(context)
            else:
                tools_context = plugin.tools_context(context)
            gpt_tools_metadata = generate_gpt_tools_schemas(
                context.app.bot_metadata, tools_context
            )
        else:
            gpt_tools_metadata = plugin._gpt_tools_metadata

        logger.debug(f"Messages: {messages}")
        logger.debug(f"GPT tools metadata: {gpt_tools_metadata}")

        response = await client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=messages,
            tools=gpt_tools_metadata,
            tool_choice="auto",
        )

        has_function_calls = False
        for output in response.choices:
            if output.message.content:
                await handle_openai_text(context=context, output=output.message)
                messages.append(output.message)
            elif output.message.tool_calls:
                tool_call = output.message.tool_calls[0]
                has_function_calls = True
                tool_call_message = {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "type": "function",
                            "id": tool_call.id,
                            "function": tool_call.function.model_dump(mode="json"),
                        }
                    ],
                }
                await add_message_log(
                    db_session=context.db_session,
                    user=context.user,
                    client_id=context.message.chat.id
                    if context.message.business_connection_id
                    else None,
                    content=json.dumps(tool_call_message, ensure_ascii=False),
                )
                messages.append(tool_call_message)
                # Execute the function call and append result to messages
                function_name = tool_call.function.name
                function_args: dict = json.loads(tool_call.function.arguments)
                function_name_parts = function_name.split("__")
                result = None
                if function_name_parts[0] == "model":
                    entity_name = function_name_parts[1]
                    crud_command = function_name_parts[2]
                    entity_descriptor = context.app.bot_metadata.entity_descriptors[
                        entity_name
                    ]
                    try:
                        if crud_command == CrudCommand.LIST:
                            result = await entity_descriptor.crud.list_all(
                                db_session=context.db_session, user=context.user
                            )
                        elif crud_command == CrudCommand.GET_BY_ID:
                            entity_id = function_args.pop("id")
                            result = await entity_descriptor.crud.get_by_id(
                                db_session=context.db_session,
                                user=context.user,
                                id=entity_id,
                            )
                        elif crud_command == CrudCommand.CREATE:
                            result = await entity_descriptor.crud.create(
                                db_session=context.db_session,
                                user=context.user,
                                model=entity_descriptor.crud.create_schema(
                                    **function_args
                                ),
                            )
                        elif crud_command == CrudCommand.UPDATE:
                            entity_id = function_args.pop("id")
                            result = await entity_descriptor.crud.update(
                                db_session=context.db_session,
                                user=context.user,
                                id=entity_id,
                                model=entity_descriptor.crud.update_schema(
                                    **function_args
                                ),
                            )
                        elif crud_command == CrudCommand.DELETE:
                            entity_id = function_args.pop("id")
                            result = await entity_descriptor.crud.delete(
                                db_session=context.db_session,
                                user=context.user,
                                id=entity_id,
                            )
                    except ForbiddenError as e:
                        result = {"error": f"Forbidden: {e}"}
                    except NotFoundError as e:
                        result = {"error": f"Not found: {e}"}
                    except Exception as e:
                        result = {"error": f"Error: {e}"}
                elif function_name_parts[0] == "process":
                    process_name = function_name_parts[1]
                    process_descriptor = context.app.bot_metadata.process_descriptors[
                        process_name
                    ]
                    try:
                        if iscoroutinefunction(process_descriptor.process_class.run):
                            result = await process_descriptor.process_class.run(
                                context,
                                parameters=process_descriptor.input_schema(
                                    **function_args
                                ),
                            )
                        else:
                            result = process_descriptor.process_class.run(
                                context,
                                parameters=process_descriptor.input_schema(
                                    **function_args
                                ),
                            )
                    except Exception as e:
                        result = {"error": f"Error: {e}"}
                # Append the function call result as assistant message
                if isinstance(result, BaseModel):
                    result = result.model_dump(mode="json")
                elif isinstance(result, list):
                    result = [item.model_dump(mode="json") for item in result]

                message = {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result),
                }
                await add_message_log(
                    db_session=context.db_session,
                    user=context.user,
                    client_id=context.message.chat.id
                    if context.message.business_connection_id
                    else None,
                    content=json.dumps(message, ensure_ascii=False),
                )
                messages.append(message)

        # If no function calls were made, break the loop
        if not has_function_calls:
            break

    if iteration >= max_iterations:
        await context.message.answer(
            "Maximum conversation iterations reached. Please try again."
        )


@router.message()
async def handle_message(
    message: Message,
    db_session: AsyncSession,
    user: UserBase,
    app: QuickBot,
    app_state: State,
) -> None:
    plugin: "AgentPlugin" = app.plugins["AgentPlugin"]

    context = BotContext(
        db_session=db_session,
        app=app,
        app_state=app_state,
        user=user,
        message=message,
    )

    await add_message_log(
        db_session=db_session,
        user=user,
        content=json.dumps(
            {"role": "user", "content": message.text}, ensure_ascii=False
        ),
    )

    system_prompt = await get_system_prompt(plugin, context)
    messages = await get_messages(plugin, context, system_prompt)

    if config.SEND_TYPING:
        await context.message.bot.send_chat_action(
            chat_id=context.message.chat.id,
            action="typing",
        )

    async with AsyncOpenAI(
        api_key=config.OPENAI_API_KEY,
    ) as client:
        await handle_openai_cycle(
            context=context,
            client=client,
            plugin=plugin,
            messages=messages,
        )


@router.business_message()
async def handle_business_message(
    message: Message,
    db_session: AsyncSession,
    user: UserBase,
    app: QuickBot,
    app_state: State,
) -> None:
    plugin: "AgentPlugin" = app.plugins["AgentPlugin"]

    context = BotContext(
        db_session=db_session,
        app=app,
        app_state=app_state,
        user=user,
        message=message,
    )

    await add_message_log(
        db_session=db_session,
        user=user,
        client_id=message.chat.id if message.business_connection_id else None,
        content=json.dumps(
            {"role": "user", "content": message.text}, ensure_ascii=False
        ),
    )

    system_prompt = await get_system_prompt(plugin, context)
    messages = await get_messages(plugin, context, system_prompt)

    if config.SEND_TYPING:
        await context.message.bot.send_chat_action(
            chat_id=context.message.chat.id,
            action="typing",
            business_connection_id=context.message.business_connection_id,
        )

    async with AsyncOpenAI(
        api_key=config.OPENAI_API_KEY,
    ) as client:
        await handle_openai_cycle(
            context=context,
            client=client,
            plugin=plugin,
            messages=messages,
        )


async def get_system_prompt(plugin: "AgentPlugin", context: BotContext) -> str:
    system_prompt = plugin.system_prompt
    if isinstance(system_prompt, LazyProxy):
        system_prompt = system_prompt.value
    elif callable(system_prompt):
        if iscoroutinefunction(system_prompt):
            system_prompt = await system_prompt(context)
        else:
            system_prompt = system_prompt(context)
    else:
        system_prompt = system_prompt

    return system_prompt


async def get_messages(
    plugin: "AgentPlugin", context: BotContext, system_prompt: str
) -> list[dict]:
    message_log = await get_message_log(
        db_session=context.db_session,
        user=context.user,
        client_id=context.message.chat.id
        if context.message.business_connection_id
        else None,
    )

    messages = [
        {"role": "system", "content": system_prompt},
    ]

    for message_log_item in message_log:
        messages.append(json.loads(message_log_item.content))

    return messages
