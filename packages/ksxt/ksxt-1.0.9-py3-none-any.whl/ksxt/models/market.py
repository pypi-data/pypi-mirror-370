from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel

from ksxt.models.common import GeneralResponse


class TradeFeeInfo(BaseModel):
    limit_bid_fee: float
    limit_ask_fee: float

    market_bid_fee: float
    market_ask_fee: float


class SecurityData(BaseModel):
    # 종목코드
    symbol: str
    # 종목이름
    name: str
    # 종목유형
    type: str

    # 매수 주문 수량 단위
    bid_qty_unit: Optional[float] = 0
    # 매도 주문 수량 단위
    ask_qty_unit: Optional[float] = 0

    # 최소 매수 주문 수량
    bid_min_qty: Optional[float] = 0
    # 최소 매도 주문 수량
    ask_min_qty: Optional[float] = 0
    # 최대 매수 주문 수량
    bid_max_qty: Optional[float] = 0
    # 최대 매도 주문 수량
    ask_max_qty: Optional[float] = 0

    # 매수 주문 금액 단위
    bid_amount_unit: Optional[float] = 0
    # 매도 주문 금액 단위
    ask_amount_unit: Optional[float] = 0

    # 최소 매수 주문 금액
    bid_min_amount: Optional[float] = 0
    # 최소 매도 주문 금액
    ask_min_amount: Optional[float] = 0
    # 최대 매수 주문 금액
    bid_max_amount: Optional[float] = 0
    # 최대 매도 주문 금액
    ask_max_amount: Optional[float] = 0

    warning_code: bool = False


class MarketInfo(BaseModel):
    market_id: str
    securities: Dict[str, SecurityData]


class HolidayInfo(BaseModel):
    date: datetime
    # 01 : 일요일 ~ 07: 토요일
    weekend: str
    is_holiday: bool


class HolidayHistory(BaseModel):
    market: List[str]
    country: str
    history: List[HolidayInfo]


class KsxtTradeFeeResponse(GeneralResponse[TradeFeeInfo]):
    pass


class KsxtSecurityResponse(GeneralResponse[SecurityData]):
    pass


class KsxtMarketResponse(GeneralResponse[MarketInfo]):
    pass


class KsxtHolidayResponse(GeneralResponse[HolidayHistory]):
    pass
