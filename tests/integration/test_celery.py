from collections.abc import Iterator

from ashka.integrations.celery import get_container, setup_dishka
from celery import Celery  # pyright: ignore[reportMissingTypeStubs]
from dishka import FromDishka, Provider
from dishka.integrations.celery import DishkaTask

from ashka.integrations import get_container as get_dispatch_container
from ashka_lifecycle import (
    make_container,
    provide,  # pyright: ignore[reportUnknownVariableType]
)
from ashka_lifecycle.entities.scope import AshkaScope


def test_celery_bootstrap_lifecycle():
    events: list[str] = []

    class AppProvider(Provider):
        @provide(scope=AshkaScope.BOOTSTRAP)
        def resource(self) -> Iterator[str]:
            events.append("initialized")
            yield "resource"
            events.append("closed")

    app = Celery("test", broker="memory://", backend="cache+memory://")
    app.conf.task_always_eager = True  # pyright: ignore[reportUnknownMemberType]
    container = make_container(AppProvider())
    setup_dishka(container, app)

    @app.task(base=DishkaTask)  # pyright: ignore[reportUntypedFunctionDecorator, reportUnknownMemberType, reportUnknownMemberType]
    def task(resource: FromDishka[str]) -> str:
        return resource

    assert get_container(app) is container
    assert get_dispatch_container(app) is container
    assert events == []

    with container:
        assert events == ["initialized"]
        assert task.delay().get() == "resource"  # pyright: ignore[reportFunctionMemberAccess]

    assert events == ["initialized", "closed"]
