from dishka import BaseScope, new_scope

__all__ = ["AshkaScope"]


class AshkaScope(BaseScope):
    BOOTSTRAP = new_scope("BOOTSTRAP")
