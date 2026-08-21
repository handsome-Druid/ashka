from subprocess import run
from sys import executable

from ashka.integrations.taskiq import get_container

from dishka import AsyncContainer, make_async_container
from dishka.integrations.taskiq import setup_dishka
from pytest import fixture
from taskiq import AsyncBroker, BrokerMessage


@fixture
def broker():
    class Broker(AsyncBroker):
        async def kick(self, message: BrokerMessage): ...

        async def listen(self):
            yield b""  # pragma: no cover

    return Broker()


@fixture
def container():
    return make_async_container()


def test_container(broker: AsyncBroker, container: AsyncContainer):
    setup_dishka(container, broker)
    assert broker.state["dishka_container"] is container
    assert get_container(broker) is container


def test_no_taskiq():
    code = """
from importlib import util

real_find_spec = util.find_spec


def find_spec(name, *args, **kwargs):
    if name == "taskiq":
        return None
    return real_find_spec(name, *args, **kwargs)


util.find_spec = find_spec

from ashka.integrations import taskiq

assert not hasattr(taskiq, "__all__")
"""
    result = run(
        [executable, "-c", code],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
