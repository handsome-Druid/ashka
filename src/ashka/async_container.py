from dishka import AsyncContainer


class AsyncContainerType(AsyncContainer):
    async def init(self) -> None:
        """
        Only available when installed with `ashka[lifecycle]`.
        """
