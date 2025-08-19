from ksxt.base.exchange import Exchange


class ComExchange(Exchange):
    def __init__(self, id: str, name: str, zone: str = "Asia/Seoul", is_dev: bool = False) -> None:
        super().__init__(id=id, name=name, zone=zone, is_dev=is_dev)

        self.is_session_alive = False
