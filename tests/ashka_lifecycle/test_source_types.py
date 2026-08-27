import gc
from typing import Generic, NewType, TypeVar

from ashka_lifecycle import AshkaScope, provide

from dishka import Container, Provider, make_container

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
