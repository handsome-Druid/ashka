from dishka import Container


class ContainerType(Container):
    def init(self): ...  # Only available when installed with `ashka[lifecycle]`.
