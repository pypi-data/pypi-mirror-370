class EntityNotFoundException(Exception):
    name: str = "EntityNotFoundException"
    status_code: int = 404

    def __init__(self, message: str) -> None:
        super().__init__(message)
