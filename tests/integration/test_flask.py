from collections.abc import Iterator

from ashka_lifecycle import (
    AshkaScope,
    provide,  # pyright: ignore[reportUnknownVariableType]
)

from ashka.integrations import get_container as get_dispatch_container
from ashka.integrations.flask import get_container, setup_dishka
from dishka import Container, FromDishka, Provider, make_container
from flask import Flask


def test_flask_bootstrap_lifecycle():
    events: list[str] = []

    class Resource:
        value = "resource"

    class AppProvider(Provider):
        @provide(scope=AshkaScope.BOOTSTRAP)
        def resource(self) -> Iterator[Resource]:
            events.append("initialized")
            yield Resource()
            events.append("closed")

    app = Flask(__name__)

    @app.get("/")
    def handle(resource: FromDishka[Resource]):
        return resource.value

    container: Container = make_container(AppProvider())
    setup_dishka(container, app, auto_inject=True)

    assert get_container(app) is container
    assert get_dispatch_container(app) is container
    assert events == []

    with container:
        assert events == ["initialized"]
        response = app.test_client().get("/")
        assert response.data == b"resource"

    assert events == ["initialized", "closed"]
