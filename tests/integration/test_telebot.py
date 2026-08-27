from collections.abc import Iterator

from ashka_lifecycle import (
    AshkaScope,
    provide,  # pyright: ignore[reportUnknownVariableType]
)

from ashka.integrations import get_container as get_dispatch_container
from ashka.integrations.telebot import get_container, setup_dishka
from dishka import Container, FromDishka, Provider, make_container
from dishka.integrations.telebot import inject
from telebot import TeleBot, types


def test_telebot_bootstrap_lifecycle():
    events: list[str] = []
    received: list[str] = []

    class Resource:
        value = "resource"

    class AppProvider(Provider):
        @provide(scope=AshkaScope.BOOTSTRAP)
        def resource(self) -> Iterator[Resource]:
            events.append("initialized")
            yield Resource()
            events.append("closed")

    bot = TeleBot("123:token", threaded=False, use_class_middlewares=True)
    container: Container = make_container(AppProvider())

    @bot.message_handler()  # pyright: ignore[reportUnknownMemberType]
    @inject
    def handle(_: object, resource: FromDishka[Resource]):
        received.append(resource.value)

    setup_dishka(container, bot)

    assert get_container(bot) is container
    assert get_dispatch_container(bot) is container
    assert events == []

    with container:
        assert events == ["initialized"]
        bot.process_new_updates(
            [
                types.Update.de_json(  # pyright: ignore[reportUnknownMemberType, reportArgumentType]
                    {
                        "update_id": 1,
                        "message": {
                            "message_id": 1,
                            "date": 0,
                            "chat": {"id": 1, "type": "private"},
                            "from": {
                                "id": 1,
                                "is_bot": False,
                                "first_name": "Test",
                            },
                            "text": "message",
                        },
                    },
                ),
            ],
        )
        assert received == ["resource"]

    assert events == ["initialized", "closed"]
