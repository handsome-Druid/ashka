from collections.abc import Callable
from functools import wraps
from importlib.util import find_spec
from typing import Concatenate, ParamSpec, TypeVar

from ashka.container import ContainerType
from ashka.integrations._dispatch import dishka_setup, get_container_

from dishka import Container


def activate(): ...


P = ParamSpec("P")
R = TypeVar("R")

if find_spec("telebot"):
    try:
        from dishka.integrations import telebot
        from telebot import TeleBot

        __all__: list[str] = ["get_container", "setup_dishka"]

        def _setup_dishka(
            setup_dishka: Callable[Concatenate[Container, TeleBot, P], R],
        ) -> Callable[Concatenate[Container, TeleBot, P], R]:
            @wraps(setup_dishka)
            def wrapped(
                container: Container,
                bot: TeleBot,
                *args: P.args,
                **kwargs: P.kwargs,
            ) -> R:
                return_: R = setup_dishka(container, bot, *args, **kwargs)
                bot.dishka_container = container  # pyright: ignore[reportAttributeAccessIssue]
                return return_

            return wrapped

        telebot.setup_dishka = setup_dishka = _setup_dishka(telebot.setup_dishka)

        @dishka_setup.register(TeleBot)
        def _dishka_setup(  # pyright: ignore[reportUnusedFunction]
            bot: TeleBot, container: Container, *args: object, **kwargs: object
        ) -> None:
            setup_dishka(container, bot, *args, **kwargs)

        @get_container_.register(TeleBot)
        def get_container(bot: TeleBot) -> ContainerType:
            return bot.dishka_container  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType, reportAttributeAccessIssue]
    except ImportError:  # pragma: no cover
        pass
