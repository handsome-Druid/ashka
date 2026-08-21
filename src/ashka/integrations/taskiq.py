from importlib.util import find_spec

from dishka import AsyncContainer

if find_spec("taskiq"):
    from dishka.integrations import taskiq
    from taskiq import AsyncBroker

    __all__ = ["get_container", "setup_dishka"]

    _setup_dishka = taskiq.setup_dishka

    def setup_dishka(
        container: AsyncContainer, broker: AsyncBroker, *args: object, **kwargs: object
    ) -> None:
        _setup_dishka(container, broker, *args, **kwargs)
        broker.state["dishka_container"] = container

    taskiq.setup_dishka = setup_dishka

    def get_container(broker: AsyncBroker) -> AsyncContainer:
        return broker.state["dishka_container"]
