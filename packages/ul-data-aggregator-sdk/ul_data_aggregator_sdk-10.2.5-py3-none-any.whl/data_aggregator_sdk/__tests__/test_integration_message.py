import pytest
from pydantic import ValidationError

from data_aggregator_sdk.integration_message import IntegrationV0MessageProfile, ProfileKind, ProfileGranulation

INTEGRATION_MESSAGE = IntegrationV0MessageProfile(type=ProfileKind.ENERGY_A_P, tariff=-1, granulation=ProfileGranulation.MINUTE_60, values=(1.1, 1.1, 1.1, 1.1, 1.1, 1.1, 1.1, 1.1, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None))  # noqa


def test_integration_message_validation() -> None:
    assert INTEGRATION_MESSAGE != IntegrationV0MessageProfile(type=ProfileKind.ENERGY_A_P, tariff=-1, granulation=ProfileGranulation.MINUTE_30, values=(None, None, None, None, None, None, None, None, 1.1, 1.1, 1.1, 1.1, 1.1, 1.1, 1.1, 1.1, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 1.1, 1.1, 1.1, 1.1, 1.1, 1.1, 1.1, 1.1, None, None, None, None, None, None, None, None))  # noqa

    with pytest.raises(ValidationError):
        IntegrationV0MessageProfile(type=ProfileKind.ENERGY_A_P, tariff=-1, granulation=ProfileGranulation.MINUTE_60, values=(None, None, None, None, None, None, None, None, 1.1, 1.1, 1.1, 1.1, 1.1, 1.1, 1.1, 1.1))
