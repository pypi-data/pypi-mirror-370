from aiogram.utils.i18n.lazy_proxy import LazyProxy
from quickbot import QuickBot, BotEntity, BotProcess
from quickbot.model.crud_command import CrudCommand
from quickbot.model.descriptors import BotContext
from typing import Callable
from .utils import generate_gpt_tools_schemas
from .handlers.messages import router as messages_router


class AgentPlugin:
    def __init__(
        self,
        system_prompt: str | LazyProxy | Callable[[BotContext], str],
        tools_context: list[type[BotEntity] | tuple[type[BotEntity], list[CrudCommand]]]
        | Callable[
            [BotContext],
            list[
                type[BotProcess]
                | type[BotEntity]
                | tuple[type[BotEntity], list[CrudCommand]]
            ],
        ]
        | None = None,
    ) -> None:
        self.system_prompt = system_prompt
        self.tools_context = tools_context
        self._gpt_tools_metadata = []

    def register(self, app: QuickBot) -> None:
        if not callable(self.tools_context):
            self._gpt_tools_metadata = generate_gpt_tools_schemas(
                app.bot_metadata, self.tools_context
            )
        messages_router.message.middleware.register(app.auth)
        messages_router.business_message.middleware.register(app.auth)
        app.dp.include_router(messages_router)
