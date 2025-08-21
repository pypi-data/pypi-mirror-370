# src/anyads/exceptions.py

class AnyAdsException(Exception):
    """Базовое исключение для всех ошибок SDK."""
    pass

class InitializationError(AnyAdsException):
    """Ошибка при инициализации или конфигурации SDK."""
    pass

class APIError(AnyAdsException):
    """Ошибка при взаимодействии с API AnyAds (например, 4xx/5xx статусы)."""
    pass