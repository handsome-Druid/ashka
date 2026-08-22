from subprocess import run
from sys import executable

from ashka.integrations.telebot import get_container

from dishka import Container, make_container
from dishka.integrations.telebot import setup_dishka
from pytest import fixture
from telebot import TeleBot


@fixture
def bot():
    return TeleBot("1:test")


@fixture
def container():
    return make_container()


def test_container(bot: TeleBot, container: Container):
    setup_dishka(container, bot)
    assert bot.dishka_container is container  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
    assert get_container(bot) is container


def test_no_telebot():
    code = """
from importlib import util

real_find_spec = util.find_spec


def find_spec(name, *args, **kwargs):
    if name == "telebot":
        return None
    return real_find_spec(name, *args, **kwargs)


util.find_spec = find_spec

from ashka.integrations import telebot

assert not hasattr(telebot, "__all__")
"""
    result = run(
        [executable, "-c", code],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
