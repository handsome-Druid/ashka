from collections.abc import Iterator

import click
from ashka.integrations import get_container as get_dispatch_container
from ashka.integrations.click import get_container, setup_dishka
from click.testing import CliRunner
from dishka import FromDishka, Provider

from ashka_lifecycle import (
    make_container,
    provide,  # pyright: ignore[reportUnknownVariableType]
)
from ashka_lifecycle.entities.scope import AshkaScope


def test_click_bootstrap_lifecycle():
    events: list[str] = []
    running_events: list[str] = []
    contexts: list[click.Context] = []

    class Resource:
        value = "resource"

    class AppProvider(Provider):
        @provide(scope=AshkaScope.BOOTSTRAP)
        def resource(self) -> Iterator[Resource]:
            events.append("initialized")
            yield Resource()
            events.append("closed")

    container = make_container(AppProvider())

    @click.group()
    @click.pass_context
    def cli(context: click.Context):
        container.init()
        setup_dishka(container, context, auto_inject=True)
        contexts.append(context)

    @cli.command()
    def resource(resource: FromDishka[Resource]):
        running_events.extend(events)
        click.echo(resource.value)

    assert events == []

    result = CliRunner().invoke(cli, ["resource"])

    assert result.exit_code == 0
    assert result.output == "resource\n"
    assert get_container(contexts[0]) is container
    assert get_dispatch_container(contexts[0]) is container
    assert running_events == ["initialized"]
    assert events == ["initialized", "closed"]
