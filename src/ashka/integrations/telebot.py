from collections.abc import Callable
from functools import wraps
from importlib.util import find_spec
from typing import Concatenate

from ashka.container import ContainerType
from ashka.integrations._dispatch import dishka_setup, get_container_
from ashka.integrations._types import P

from dishka import Container

if find_spec("telebot"):
    try:
        from dishka.integrations import telebot
        from telebot import TeleBot

        __all__: list[str] = ["get_container", "setup_dishka"]

        _setup_dishka: Callable[..., Container] = telebot.setup_dishka

        def _dishka_setup_(
            _setup_dishka: Callable[Concatenate[Container, TeleBot, P], Container],
        ):
            @wraps(_setup_dishka)
            def inner(
                bot: TeleBot,
                container: Container,
                *args: P.args,
                **kwargs: P.kwargs,
            ) -> None:
                _setup_dishka(container, bot, *args, **kwargs)
                bot.dishka_container = container  # pyright: ignore[reportAttributeAccessIssue]

            return inner

        def setup_dishka_(
            _dishka_setup: Callable[Concatenate[TeleBot, Container, P], None],
        ):
            @wraps(_dishka_setup)
            def inner(
                container: Container,
                bot: TeleBot,
                *args: P.args,
                **kwargs: P.kwargs,
            ) -> Container:
                _dishka_setup(bot, container, *args, **kwargs)
                return container

            return inner

        dishka_setup.register(TeleBot)(_dishka_setup := _dishka_setup_(_setup_dishka))

        telebot.setup_dishka = (setup_dishka := setup_dishka_(_dishka_setup))

        @get_container_.register(TeleBot)
        def get_container(bot: TeleBot) -> ContainerType:
            return bot.dishka_container  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType, reportAttributeAccessIssue]
    except ImportError:  # pragma: no cover
        pass
