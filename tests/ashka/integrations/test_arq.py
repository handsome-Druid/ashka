from subprocess import run
from sys import executable

from ashka.integrations.arq import get_container, setup_dishka

from arq import Worker
from dishka import AsyncContainer, make_async_container
from dishka.integrations.arq import DISHKA_APP_CONTAINER_KEY
from pytest import fixture


@fixture
def worker_settings():
    async def task(ctx: dict[object, object]): ...

    return Worker([task])


@fixture
def async_container():
    return make_async_container()


def test_worker(worker_settings: Worker, async_container: AsyncContainer):
    setup_dishka(async_container, worker_settings)
    assert worker_settings.ctx[DISHKA_APP_CONTAINER_KEY] is async_container
    assert get_container(worker_settings) is async_container


def test_dict(async_container: AsyncContainer):
    worker_settings: dict[str, dict[str, AsyncContainer]] = {}
    setup_dishka(async_container, worker_settings)
    assert worker_settings["ctx"][DISHKA_APP_CONTAINER_KEY] is async_container
    assert get_container(worker_settings) is async_container


def test_no_arq():
    code = """
from importlib import util

real_find_spec = util.find_spec


def find_spec(name, *args, **kwargs):
    if name == "arq":
        return None
    return real_find_spec(name, *args, **kwargs)


util.find_spec = find_spec

from ashka.integrations import arq

assert not hasattr(arq, "__all__")
"""
    result = run(
        [executable, "-c", code],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
