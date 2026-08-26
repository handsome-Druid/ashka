from collections.abc import Callable
from importlib.util import find_spec

from ashka.container import ContainerType
from ashka.integrations._dispatch import dishka_setup, get_container_

from dishka import Container

if find_spec("telebot"):
    try:
        from dishka.integrations import telebot
        from telebot import TeleBot

        __all__: list[str] = ["get_container", "setup_dishka"]

        _setup_dishka: Callable[..., Container] = telebot.setup_dishka

        @dishka_setup.register(TeleBot)
        def _dishka_setup(
            bot: TeleBot, container: Container, *args: object, **kwargs: object
        ) -> None:
            _setup_dishka(container, bot, *args, **kwargs)
            bot.dishka_container = container  # pyright: ignore[reportAttributeAccessIssue]

        def setup_dishka(
            container: Container, bot: TeleBot, *args: object, **kwargs: object
        ) -> None:
            _dishka_setup(bot, container, *args, **kwargs)

        telebot.setup_dishka = setup_dishka

        @get_container_.register(TeleBot)
        def get_container(bot: TeleBot) -> ContainerType:
            return bot.dishka_container  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType, reportAttributeAccessIssue]
    except ImportError:  # pragma: no cover
        pass
