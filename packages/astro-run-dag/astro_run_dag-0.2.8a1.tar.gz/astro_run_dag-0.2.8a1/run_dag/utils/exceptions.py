class ConnectionFailed(Exception):
    """An exception raised when the sql file's connection cannot be established."""

    def __init__(self, *args: object, conn_id: str) -> None:
        self.conn_id = conn_id
        super().__init__(*args)
