from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from ksxt.models.common import GeneralResponse


class OrderBase(BaseModel):
    datetime: datetime
    order_id: str
    symbol: str
    name: str
    price: float
    qty: float


class CreateOrderResponse(BaseModel):
    order_datetime: datetime
    order_id: str


class CancelOrderResponse(BaseModel):
    order_datetime: datetime
    order_id: str


class ModifyOrderResponse(BaseModel):
    order_datetime: datetime
    order_id: str


# Orders에 대한 구체적인 Response 타입
class KsxtCreateOrderResponse(GeneralResponse[CreateOrderResponse]):
    pass


class KsxtCancelOrderResponse(GeneralResponse[CancelOrderResponse]):
    pass


class KsxtModifyOrderResponse(GeneralResponse[ModifyOrderResponse]):
    pass
