from typing import Any


class AppException(Exception):
    def __init__(
        self,
        *,
        status_code: int,
        code: str,
        message: str,
        details: Any | None = None,
    ) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details
        super().__init__(message)


class UnauthorizedError(AppException):
    def __init__(self, message: str = "Autenticação necessária.", code: str = "unauthorized") -> None:
        super().__init__(status_code=401, code=code, message=message)


class ForbiddenError(AppException):
    def __init__(self, message: str = "Acesso negado a este recurso.", code: str = "forbidden") -> None:
        super().__init__(status_code=403, code=code, message=message)


class NotFoundError(AppException):
    def __init__(self, message: str = "Recurso não encontrado.", code: str = "not_found") -> None:
        super().__init__(status_code=404, code=code, message=message)


class ConflictError(AppException):
    def __init__(self, message: str = "Conflito de dados.", code: str = "conflict") -> None:
        super().__init__(status_code=409, code=code, message=message)


class ValidationAppError(AppException):
    def __init__(self, message: str = "Dados inválidos.", code: str = "validation_error") -> None:
        super().__init__(status_code=422, code=code, message=message)


class RateLimitError(AppException):
    def __init__(
        self,
        message: str = "Muitas tentativas. Aguarde alguns instantes.",
        code: str = "rate_limited",
    ) -> None:
        super().__init__(status_code=429, code=code, message=message)

