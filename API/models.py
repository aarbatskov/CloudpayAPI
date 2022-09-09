from dataclasses import dataclass, field
from datetime import datetime
import marshmallow_dataclass
import marshmallow.validate
from marshmallow import EXCLUDE
from marshmallow_dataclass import NewType


class BaseModel:

    @classmethod
    def _get_schema(cls):
        return marshmallow_dataclass.class_schema(cls)(unknown=EXCLUDE)

    @classmethod
    def create(cls, data: dict):
        return cls._get_schema().load(data)

    def to_dict(self):
        return self._get_schema().dump(self)


@dataclass
class Transaction(BaseModel):
    code: int = field(metadata=dict(data_key="ReasonCode"))
    public_id: str = field(metadata=dict(data_key="PublicId"))
    terminal_url: str = field(metadata=dict(data_key="TerminalUrl"))
    transaction_id: int = field(metadata=dict(data_key="TransactionId"))
    amount: float = field(metadata=dict(data_key="Amount"))
    currency: str = field(metadata=dict(data_key="Currency"))
    currency_code: int = field(metadata=dict(data_key="CurrencyCode"))
    payment_amount: int = field(metadata=dict(data_key="PaymentAmount"))
    payment_currency: str = field(metadata=dict(data_key="PaymentCurrency"))
    payment_currency_code: int = field(metadata=dict(data_key="PaymentCurrencyCode"))
    invoice_id: int = field(
        metadata=dict(
            data_key="InvoiceId", required=False, allow_none=True
        )
    )
    account_id: str = field(
        metadata=dict(
            data_key="AccountId", required=False, allow_none=True
        )
    )
    email = NewType("Email", str, field=marshmallow.fields.Email, required=False, allow_none=True)
    json_data: dict = field(
        metadata=dict(
            data_key="JsonData", required=False, allow_none=True
        )
    )
    created_data: datetime = field(metadata=dict(data_key="CreatedDateIso"))
    auth_code: str = field(metadata=dict(data_key="AuthCode"))
    test_mode: bool = field(metadata=dict(data_key="TestMode"))
    ip_address: str = field(metadata=dict(data_key="IpAddress"))
    ip_latitude: float = field(metadata=dict(data_key="IpLatitude"))
    ip_longitude: float = field(metadata=dict(data_key="IpLongitude"))
    card_first_six: str = field(metadata=dict(data_key="CardFirstSix"))
    card_last_four: int = field(metadata=dict(data_key="CardLastFour"))
    status: str = field(metadata=dict(data_key="Status"))
    status_code: int = field(metadata=dict(data_key="StatusCode"))
    token: str = field(metadata=dict(data_key="Token", required=False))


@dataclass
class Secure3D(BaseModel):
    transaction_id: str = field(metadata=dict(data_key="TransactionId"))
    pa_req: str = field(metadata=dict(data_key="PaReq"))
    go_req: str = field(metadata=dict(data_key="GoReq"))
    acs_url: str = field(metadata=dict(data_key="AcsUrl"))
