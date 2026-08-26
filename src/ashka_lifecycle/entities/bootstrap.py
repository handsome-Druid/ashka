from types import FunctionType
from weakref import WeakSet

bootstrap_types: WeakSet[FunctionType] = WeakSet()
