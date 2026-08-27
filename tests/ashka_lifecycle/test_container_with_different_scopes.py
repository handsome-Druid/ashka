from ashka import AshkaScope, provide
from dishka import Provider, Scope, make_async_container, make_container
from pytest import LogCaptureFixture, mark

result = 0


class P(Provider):
    @provide(scope=AshkaScope.BOOTSTRAP, provides=None)
    @staticmethod
    def bootstrap():
        global result
        result += 1
        yield
        result -= 1


def test_container(caplog: LogCaptureFixture):
    assert result == 0
    with make_container(P(), start_scope=Scope.RUNTIME):
        assert result == 0
    assert result == 0
    caplog.clear()
    make_container(P(), start_scope=Scope.RUNTIME).init()  # pyright: ignore[reportAttributeAccessIssue]
    assert "RUNTIME" in caplog.text
    with make_container(P(), start_scope=Scope.APP):
        assert result == 1
    assert result == 0
    with make_container(P(), start_scope=Scope.SESSION):
        assert result == 0
    assert result == 0
    with make_container(P(), start_scope=Scope.REQUEST):
        assert result == 0
    assert result == 0
    with make_container(P(), start_scope=Scope.ACTION):
        assert result == 0
    assert result == 0
    with make_container(P(), start_scope=Scope.STEP):
        assert result == 0
    assert result == 0


@mark.asyncio
async def test_async_container(caplog: LogCaptureFixture):
    assert result == 0
    async with make_async_container(P(), start_scope=Scope.RUNTIME):
        assert result == 0
    assert result == 0
    caplog.clear()
    await make_async_container(P(), start_scope=Scope.RUNTIME).init()  # pyright: ignore[reportAttributeAccessIssue]
    assert "RUNTIME" in caplog.text
    async with make_async_container(P(), start_scope=Scope.APP):
        assert result == 1
    assert result == 0
    async with make_async_container(P(), start_scope=Scope.SESSION):
        assert result == 0
    assert result == 0
    async with make_async_container(P(), start_scope=Scope.REQUEST):
        assert result == 0
    assert result == 0
    async with make_async_container(P(), start_scope=Scope.ACTION):
        assert result == 0
    assert result == 0
    async with make_async_container(P(), start_scope=Scope.STEP):
        assert result == 0
    assert result == 0
