"""Исключения для Marketplace API"""


class MarketplaceAPIException(Exception):
    """Базовое исключение для всех ошибок API"""
    pass


class APIError(MarketplaceAPIException):
    """Ошибка API запроса"""

    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code


class AuthError(MarketplaceAPIException):
    """Ошибка аутентификации"""
    pass


class ForbiddenError(MarketplaceAPIException):
    """Ошибка аутентификации"""
    pass


class ValidationError(MarketplaceAPIException):
    """Ошибка валидации данных"""
    pass
