from pydantic import BaseModel, model_validator
from typing import List

from ksxt.models.common import GeneralResponse


class BalanceData(BaseModel):
    symbol: str
    name: str

    price: float
    evaluation_price: float

    qty: float
    free_qty: float
    used_qty: float

    amount: float | None = 0.0
    evaluation_amount: float | None = 0.0
    pnl: float | None = 0.0
    pnl_ratio: float | None = 0.0

    @model_validator(mode="after")
    def calculate_fields(cls, values):
        values.amount = values.price * values.qty
        values.evaluation_amount = values.evaluation_price * values.qty
        values.pnl = values.evaluation_price - values.price
        values.pnl_ratio = values.pnl / values.price if values.price != 0 else 0.0
        return values


class BalanceInfo(BaseModel):
    currency: str
    total_amount: float
    total_evaluation_amount: float
    total_pnl_amount: float
    total_pnl_ratio: float
    balances: List[BalanceData]


# Balance에 대한 구체적인 Response 타입
class KsxtBalanceResponse(GeneralResponse[BalanceInfo]):
    pass
