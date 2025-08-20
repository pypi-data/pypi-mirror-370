from datetime import date, datetime
from typing import Dict, Any, Optional, Union


def get_query_params(
    period_from: Optional[Union[datetime, date]],
    period_to: Optional[Union[datetime, date]],
    limit: Optional[int],
    offset: Optional[int],
) -> Dict[str, Any]:

    query_params = dict()
    if period_from is not None:
        query_params.update({"period_from": period_from})

    if period_to is not None:
        query_params.update({"period_to": period_to})

    if limit is not None:
        query_params.update({"limit": limit})  # type: ignore

    if offset is not None:
        query_params.update({"offset": offset})  # type: ignore
    return query_params
