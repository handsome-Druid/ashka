from importlib.util import find_spec

from dishka import Container

from ._dispatch import dishka_setup, get_container_

if find_spec("click"):
    from click import Context
    from dishka.integrations import click

    __all__ = ["get_container", "setup_dishka"]

    @dishka_setup.register(Context)
    def _dishka_setup(
        context: Context, container: Container, *args: object, **kwargs: object
    ):
        click.setup_dishka(container, context, *args, **kwargs)

    setup_dishka = click.setup_dishka

    @get_container_.register(Context)
    def get_container(context: Context) -> Container:
        return context.meta[click.CONTAINER_NAME]
