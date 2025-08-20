from fastapi import HTTPException, status


class CustomHTTPException(HTTPException):
    def __init__(self, message: str, status: int, code: str = None, additional_info: dict = None):
        super().__init__(status_code=status, detail=message)

        self.code = code
        self.message = message
        self.status = status
        self.additional_info = additional_info


class NotAuthorizedException(CustomHTTPException):
    def __init__(self, message: str = "You are not authorized", status: int = 401, code: str = None,
                 additional_info: dict = None):
        super().__init__(message=message, status=status, code=code, additional_info=additional_info)


class ForbiddenException(CustomHTTPException):
    def __init__(self, message: str = "Permission denied", status: int = 403, code: str = None,
                 additional_info: dict = None):
        super().__init__(message=message, status=status, code=code, additional_info=additional_info)


class BadRequestException(CustomHTTPException):
    def __init__(self, message: str = "Bad request", status: int = 400, code: str = None,
                 additional_info: dict = None):
        super().__init__(message=message, status=status, code=code, additional_info=additional_info)


class NotFoundException(CustomHTTPException):
    def __init__(self, message: str = "Not found", status: int = 404, code: str = None,
                 additional_info: dict = None):
        super().__init__(message=message, status=status, code=code, additional_info=additional_info)


class InternalException(CustomHTTPException):
    def __init__(self, message: str = "Internal exception", status: int = 500, code: str = None,
                 additional_info: dict = None):
        super().__init__(message=message, status=status, code=code, additional_info=additional_info)
