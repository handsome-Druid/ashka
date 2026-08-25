from importlib.util import find_spec

from ashka.container import ContainerType
from ashka.integrations._dispatch import dishka_setup, get_container_

from dishka import Container

if find_spec("click"):
    try:
        from click import Context
        from dishka.integrations import click

        __all__: list[str] = ["get_container", "setup_dishka"]

        @dishka_setup.register(Context)
        def _dishka_setup(  # pyright: ignore[reportUnusedFunction]
            context: Context, container: Container, *args: object, **kwargs: object
        ) -> None:
            click.setup_dishka(container, context, *args, **kwargs)

        setup_dishka = click.setup_dishka

        @get_container_.register(Context)
        def get_container(context: Context) -> ContainerType:
            return context.meta[click.CONTAINER_NAME]
    except ImportError:  # pragma: no cover
        pass
