class DataAggregatorAbstractError(Exception):
    """
    Ошибки которые наследуются от этого класса используются
    - для отделения ошибок НАШЕГО приложения от всех других.
    АБСТРАКТНЫЙ КЛАСС = НАПРЯМУЮ НЕ ИСПОЛЬЗУЕТСЯ для raise
    """
    def __init__(self, message: str, error: Exception, status_code: int) -> None:
        assert isinstance(message, str), f'message must be str. "{type(message).__name__}" was given'
        assert isinstance(error, Exception), f'error must be Exception. "{type(error).__name__}" was given'
        super(DataAggregatorAbstractError, self).__init__(f'{message} :: {str(error)} :: {status_code})')
        self.status_code = status_code
        self.error = error


class DataAggregatorRequestError(DataAggregatorAbstractError):
    pass


class DataAggregatorResponseError(DataAggregatorAbstractError):
    pass
