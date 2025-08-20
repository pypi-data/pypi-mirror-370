from functools import wraps
from typing import Any, Callable, Dict, List, TypeVar

from ul_api_utils.errors import Client4XXInternalApiError, Server5XXInternalApiError, \
    ResponseJsonInternalApiError, NotFinishedRequestInternalApiError

from data_aggregator_sdk.errors import DataAggregatorRequestError, DataAggregatorResponseError

TKwargs = TypeVar('TKwargs', bound=Dict[str, Any])

STDResp = TypeVar('STDResp', bound=Dict[str, Any] | List[Dict[str, Any]])    # TODO:  Dict[str, Any] -> JsonApiResponsePayload

TFn = Callable[..., STDResp]


def internal_api_error_handler_old(api_method_fn: TFn) -> TFn:      # type: ignore
    ''' BROKEN TYPING '''       # TODO: must be updated to typed internal_api_error_handler
    @wraps(api_method_fn)
    def error_handler_wrapper(*args: Any, **kwargs: TKwargs) -> STDResp:    # type: ignore
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
    return error_handler_wrapper
