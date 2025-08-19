from pydantic import BaseModel
from typing import Dict, List

from ksxt.models.common import GeneralResponse


class OrderBookData(BaseModel):
    side: str
    ob_num: int
    ob_price: float
    ob_qty: float


class OrderBookInfo(BaseModel):
    total_asks_qty: float
    total_bids_qty: float
    asks: List[OrderBookData]
    bids: List[OrderBookData]


class MultiSymbolOrderBookInfos(BaseModel):
    order_books: Dict[str, OrderBookInfo]


# Single symbol OrderBook에 대한 구체적인 Response 타입
class KsxtSingleOrderBookResponse(GeneralResponse[OrderBookInfo]):
    pass


# Multi symbol OrderBook에 대한 구체적인 Response 타입
class KsxtMultiOrderBookResponse(GeneralResponse[MultiSymbolOrderBookInfos]):
    pass
