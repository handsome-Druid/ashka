from subprocess import run
from sys import executable

from ashka.integrations.aiogram import get_container

from aiogram import Router
from dishka import AsyncContainer, make_async_container
from dishka.integrations.aiogram import setup_dishka
from pytest import fixture


@fixture
def router():
    return Router()


@fixture
def container():
    return make_async_container()


def test_container(router: Router, container: AsyncContainer):
    setup_dishka(container, router)
    assert router.dishka_container is container  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
    assert get_container(router) is container


def test_no_aiogram():
    code = """
from importlib import util

real_find_spec = util.find_spec


def find_spec(name, *args, **kwargs):
    if name == "aiogram":
        return None
    return real_find_spec(name, *args, **kwargs)


util.find_spec = find_spec

from ashka.integrations import aiogram

assert not hasattr(aiogram, "__all__")
"""
    result = run(
        [executable, "-c", code],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
