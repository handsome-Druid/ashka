from ashka import AshkaScope, provide
from dishka import Provider
from dishka.provider.exceptions import MissingReturnHintError
from pytest import raises


def test_missing():
    with raises(MissingReturnHintError):

        class P(Provider):
            @provide(scope=AshkaScope.BOOTSTRAP)
            @staticmethod
            def bootstarp(): ...
