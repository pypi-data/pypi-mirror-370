from functools import wraps
from typing import Any, Callable, Dict, List, TypeVar, cast

from ul_api_utils.errors import Client4XXInternalApiError, Server5XXInternalApiError, \
    ResponseJsonInternalApiError, NotFinishedRequestInternalApiError

from data_aggregator_sdk.errors import DataAggregatorRequestError, DataAggregatorResponseError

TKwargs = TypeVar('TKwargs', bound=Dict[str, Any])

STDResp = TypeVar('STDResp', bound=Dict[str, Any] | List[Dict[str, Any]])    # TODO:  Dict[str, Any] -> JsonApiResponsePayload

TFn = TypeVar('TFn', bound=Callable)        # type: ignore


def internal_api_error_handler(api_method_fn: TFn) -> TFn:
    @wraps(api_method_fn)
    def error_handler_wrapper(*args: Any, **kwargs: TKwargs) -> TFn:
        try:
            return api_method_fn(*args, **kwargs)
        except Client4XXInternalApiError as e:
            raise DataAggregatorRequestError(str(e), e, e.status_code)
        except Server5XXInternalApiError as e:
            raise DataAggregatorResponseError(str(e), e, e.status_code)
        except ResponseJsonInternalApiError as e:
            raise DataAggregatorResponseError(str(e), e, 500)
        except NotFinishedRequestInternalApiError as e:
            raise DataAggregatorResponseError("SERVICE TEMPORARY UNAVAIBLE", e, 503)
    return cast(TFn, error_handler_wrapper)
