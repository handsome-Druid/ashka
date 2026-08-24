from dishka import AsyncContainer


class AsyncContainerType(AsyncContainer):
    async def init(self): ...  # Only available when installed with `ashka[lifecycle]`.
