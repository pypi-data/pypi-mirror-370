from datetime import datetime
from typing import List
from pydantic import BaseModel

from ksxt.models.common import GeneralResponse


class TransactionInfo(BaseModel):
    # 주문 고유 아이디
    uuid: str
    # 계좌 번호
    account_id: str | None = None

    # 주문 종류 (ask, bid, deposit, withdrawal)
    transaction_type: str

    # order type (limit, market, default)
    order_type: str | None = None

    # position (long, short)
    tr_position: str | None = None

    # 종목 정보
    symbol: str
    # 가격
    price: float
    # 수량
    qty: float
    # 금액
    amount: float

    # 세금
    tax: float | None = 0
    # 수수료
    fee: float | None = 0

    # 화폐 통화 정보
    currency: str | None = None

    # 주문 생성 시간
    created_at: datetime


class WithdrawalHistory(BaseModel):
    history: List[TransactionInfo]


class DepositHistory(BaseModel):
    history: List[TransactionInfo]


class OpenedOrderHistory(BaseModel):
    history: List[TransactionInfo]


class ClosedOrderHistory(BaseModel):
    history: List[TransactionInfo]


class KsxtWithdrawalHistoryResponse(GeneralResponse[WithdrawalHistory]):
    pass


class KsxtDepositHistoryResponse(GeneralResponse[DepositHistory]):
    pass


class KsxtOpenOrderResponse(GeneralResponse[OpenedOrderHistory]):
    pass


class KsxtClosedOrderResponse(GeneralResponse[ClosedOrderHistory]):
    pass
