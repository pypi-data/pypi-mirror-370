from datetime import datetime
from typing import Dict
from pydantic import BaseModel

from ksxt.models.common import GeneralResponse


class TickerInfo(BaseModel):
    symbol: str
    price: float
    ts: datetime


class MultiSymbolTickerInfo(BaseModel):
    tickers: Dict[str, TickerInfo]


# 단일 Ticker에 대한 Response 타입
class KsxtTickerResponse(GeneralResponse[TickerInfo]):
    pass


# 복수 Ticker에 대한 Response 타입
class KsxtTickersResponse(GeneralResponse[MultiSymbolTickerInfo]):
    pass
