from fastapi import HTTPException, status

class GenericException(HTTPException):
    def __init__(self, detail: str = "An error occurred"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class EntityNotFoundException(HTTPException):
    def __init__(self, entity: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=f"{entity} not found")
