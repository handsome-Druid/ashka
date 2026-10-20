import gc
from typing import Generic, NewType, TypeVar

from ashka_lifecycle import AshkaScope, provide

import pytest
from dishka import BaseScope, Container, Provider, Scope, make_container

SourceType = TypeVar("SourceType")
BuiltinResult = NewType("BuiltinResult", bool)

created: set[str] = set()


class ClassSource:
    def __init__(self):
        created.add("class")


class GenericClassSource(Generic[SourceType]):
    def __init__(self):
        created.add("generic_class")


class FunctionResult: ...


class ClassmethodResult: ...


class StaticmethodResult: ...


class CallableResult: ...


class CallableSource:
    def __call__(self) -> CallableResult:
        created.add("callable")
        return CallableResult()


class SourceTypesProvider(Provider):
    class_source = provide(ClassSource, scope=AshkaScope.BOOTSTRAP)
    generic_class_source = provide(GenericClassSource[int], scope=AshkaScope.BOOTSTRAP)

    @provide(scope=AshkaScope.BOOTSTRAP)
    def function_source(self) -> FunctionResult:
        created.add("function")
        return FunctionResult()

    @provide(scope=AshkaScope.BOOTSTRAP)
    @classmethod
    def classmethod_source(cls) -> ClassmethodResult:
        created.add("classmethod")
        return ClassmethodResult()

    builtin_source = provide(
        gc.isenabled,
        scope=AshkaScope.BOOTSTRAP,
        provides=BuiltinResult,
    )

    @provide(scope=AshkaScope.BOOTSTRAP)
    @staticmethod
    def staticmethod_source() -> StaticmethodResult:
        created.add("staticmethod")
        return StaticmethodResult()

    callable_source = provide(CallableSource(), scope=AshkaScope.BOOTSTRAP)


def test_bootstrap_source_types():
    created.clear()
    container: Container = make_container(SourceTypesProvider())

    with container:
        assert created == {
            "callable",
            "class",
            "classmethod",
            "function",
            "generic_class",
            "staticmethod",
        }
        assert container.get(BuiltinResult) is gc.isenabled()


@pytest.mark.parametrize("scope", [Scope.APP, AshkaScope.BOOTSTRAP])
@pytest.mark.parametrize("source_kind", ["class", "function", "explicit_provides"])
def test_provide_keyword_source(source_kind: str, scope: BaseScope):
    created.clear()

    def create_source() -> ClassSource:
        return ClassSource()

    if source_kind == "explicit_provides":
        factory = provide(
            source=staticmethod(create_source),
            scope=scope,
            provides=ClassSource,
        )
    else:
        source = ClassSource if source_kind == "class" else staticmethod(create_source)
        factory = provide(source=source, scope=scope)

    class KeywordSourceProvider(Provider):
        value = factory

    container = make_container(KeywordSourceProvider())
    assert created == set()

    with container:
        assert created == ({"class"} if scope is AshkaScope.BOOTSTRAP else set())
        value = container.get(ClassSource)
        assert isinstance(value, ClassSource)
        assert created == {"class"}
        assert container.get(ClassSource) is value
