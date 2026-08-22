from subprocess import run
from sys import executable
from unittest.mock import Mock

from ashka import make_async_container
from ashka.integrations.faststream import (
    get_container,
    setup_dishka,  # pyright: ignore[reportUnknownVariableType]
)

from faststream import FastStream
from faststream._internal.broker import BrokerUsecase


def test_app_setup():
    broker = Mock(spec=BrokerUsecase)
    app = FastStream(broker)
    container = make_async_container()

    setup_dishka(container, app=app)

    assert get_container(app) is container


def test_broker_setup():
    broker = Mock(spec=BrokerUsecase)
    container = make_async_container()

    setup_dishka(container, broker=broker)

    assert get_container(broker) is container


def test_import_after_dishka():
    result = run(
        [
            executable,
            "-c",
            "import dishka.integrations.faststream; import ashka.integrations.faststream",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert "was imported before" in result.stderr
