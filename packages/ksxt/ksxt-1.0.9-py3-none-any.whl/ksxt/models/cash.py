from pydantic import BaseModel

from ksxt.models.common import GeneralResponse


class CashInfo(BaseModel):
    currency: str
    cash: float
    cash_d1: float
    cash_d2: float


# Cash에 대한 구체적인 Response 타입
class KsxtCashResponse(GeneralResponse[CashInfo]):
    pass
