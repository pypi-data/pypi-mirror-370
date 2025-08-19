class Exceptions:
    class ErrorConnection(Exception):
        """Ошибка подключения к серверу."""
        def __init__(self, message="Ошибка подключения к серверу"):
            super().__init__(message)
    
    class UnexpectedError(Exception):
        """Неожиданная ошибка при подключении к серверу."""
        def __init__(self, message="Неожиданная ошибка при подключении к серверу"):
            super().__init__(message)
    
    class ServerTimeoutError(Exception):
        """Тайм-аут подключения к серверу."""
        def __init__(self, message="Тайм-аут подключения к серверу"):
            super().__init__(message)
    
    class ServerAccessDeniedError(Exception):
        """Доступ к серверу отклонён."""
        def __init__(self, message="Доступ к серверу отклонён"):
            super().__init__(message)
    
    class ServerNotFoundError(Exception):
        """Сервер не найден."""
        def __init__(self, message="Сервер не найден"):
            super().__init__(message)
    
    class ServerFailureError(Exception):
        """Сбой на сервере."""
        def __init__(self, message="Сбой на сервере"):
            super().__init__(message)
    
    class InvalidServerResponseError(Exception):
        """Некорректный ответ от сервера."""
        def __init__(self, message="Некорректный ответ от сервера"):
            super().__init__(message)
    class CertificateVerifyFailed(Exception):
        """[SSL: CERTIFICATE_VERIFY_FAILED]"""
        def __init__(self, message="[SSL: CERTIFICATE_VERIFY_FAILED]"):
            super().__init__(message)
    class DNS:
        class ErrorConnection(Exception):
            """Ошибка подключения к DNS-серверу."""
            def __init__(self, message="Ошибка подключения к DNS-серверу"):
                super().__init__(message)

        class UnexpectedError(Exception):
            """Неожиданная ошибка при работе с DNS."""
            def __init__(self, message="Неожиданная ошибка при работе с DNS"):
                super().__init__(message)

        class DNSServerNotFoundError(Exception):
            """DNS-сервер не найден."""
            def __init__(self, message="DNS-сервер не найден"):
                super().__init__(message)

        class DNSTimeoutError(Exception):
            """Таймаут при запросе к DNS-серверу."""
            def __init__(self, message="Таймаут при запросе к DNS-серверу"):
                super().__init__(message)

        class InvalidDNSError(Exception):
            """Неверный формат DNS-запроса."""
            def __init__(self, message="Неверный формат DNS-запроса"):
                super().__init__(message)

        class DNSResponseError(Exception):
            """Ошибка в ответе от DNS-сервера."""
            def __init__(self, message="Ошибка в ответе от DNS-сервера"):
                super().__init__(message)

        class DNSServerFailureError(Exception):
            """Отказ DNS-сервера."""
            def __init__(self, message="Отказ DNS-сервера"):
                super().__init__(message)

        class DNSAccessDeniedError(Exception):
            """Доступ к DNS-серверу запрещён."""
            def __init__(self, message="Доступ к DNS-серверу запрещён"):
                super().__init__(message)


