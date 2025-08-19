from datetime import datetime
from typing import Dict, List, Optional
import inspect

from ksxt.models.balance import BalanceData, BalanceInfo
from ksxt.models.cash import CashInfo
from ksxt.models.historical import HistoricalDataInfo, OHLCVData
from ksxt.models.market import HolidayHistory, HolidayInfo, MarketInfo, SecurityData, TradeFeeInfo
from ksxt.models.order import CancelOrderResponse, CreateOrderResponse, ModifyOrderResponse
from ksxt.models.orderbook import MultiSymbolOrderBookInfos, OrderBookData, OrderBookInfo
from ksxt.models.ticker import MultiSymbolTickerInfo, TickerInfo
from ksxt.models.transaction import (
    ClosedOrderHistory,
    DepositHistory,
    OpenedOrderHistory,
    TransactionInfo,
    WithdrawalHistory,
)


class BaseParser:
    def _raise_not_implemented_error(self):
        caller = inspect.stack()[1].function
        raise NotImplementedError(f"{self.__class__.__name__} called {caller}")

    def parse_markets(self, response: List[Dict], base_market: str = "KRW") -> MarketInfo:
        self._raise_not_implemented_error()

    def _parse_market(self, market: Dict) -> SecurityData:
        self._raise_not_implemented_error()

    def parse_historical_data(
        self,
        response: List[Dict],
        symbol: str,
        start: datetime | None = None,
        end: datetime | None = None,
        base_market: str = "KRW",
    ) -> HistoricalDataInfo:
        self._raise_not_implemented_error()

    def _parse_ohlcva(self, ohlcva: dict, base_market: str = "KRW") -> OHLCVData:
        self._raise_not_implemented_error()

    def parse_historical_index_data(self, response: dict, symbol: str, base_market: str = "KRW") -> HistoricalDataInfo:
        self._raise_not_implemented_error()

    def _parse_index_ohlcva(self, ohlcva: dict, base_market: str = "KRW") -> OHLCVData:
        self._raise_not_implemented_error()

    def parse_ticker(self, response: List[Dict], base_market: str = "KRW") -> TickerInfo:
        self._raise_not_implemented_error()

    def parse_tickers(self, response: List[Dict], base_market: str = "KRW") -> MultiSymbolTickerInfo:
        self._raise_not_implemented_error()

    def _parse_ticker(self, response: dict, base_market: str) -> TickerInfo:
        self._raise_not_implemented_error()

    def parse_orderbook(self, response: List[Dict], base_market: str = "KRW") -> OrderBookInfo:
        self._raise_not_implemented_error()

    def parse_orderbooks(self, response: dict, base_market: str) -> MultiSymbolOrderBookInfos:
        self._raise_not_implemented_error()

    def _parse_orderbook(
        self, orderbook: dict, index: int, base_market: str = "KRW"
    ) -> tuple[OrderBookData, OrderBookData]:
        self._raise_not_implemented_error()

    def parse_balance(
        self,
        response: List[Dict],
        base_market: str = "KRW",
        excluded_symbols: Optional[list[str]] = None,
        included_symbols: list[str] | None = None,
        filter_delisted: bool = True,
        min_amount: float = 0,
    ) -> BalanceInfo:
        self._raise_not_implemented_error()

    def _parse_balance(self, data: Dict, base_market: str = "KRW") -> BalanceData:
        self._raise_not_implemented_error()

    def parse_cash(self, response: List[Dict], base_market: str = "KRW") -> CashInfo:
        self._raise_not_implemented_error()

    def parse_security(self, response: dict, base_market: str = "KRW") -> SecurityData:
        self._raise_not_implemented_error()

    def parse_trade_fee(self, response: dict, base_market: str = "KRW") -> TradeFeeInfo:
        self._raise_not_implemented_error()

    def parse_open_order_history(
        self, response: List[Dict], start: datetime | None = None, end: datetime | None = None, base_market: str = "KRW"
    ) -> OpenedOrderHistory:
        self._raise_not_implemented_error()

    def _parse_open_order_info(self, order: dict, base_market: str = "KRW") -> TransactionInfo:
        self._raise_not_implemented_error()

    def parse_closed_order_history(
        self, response: List[Dict], start: datetime | None = None, end: datetime | None = None, base_market: str = "KRW"
    ) -> ClosedOrderHistory:
        self._raise_not_implemented_error()

    def _parse_closed_order_info(self, order: dict, base_market: str = "KRW") -> TransactionInfo:
        self._raise_not_implemented_error()

    def parse_modify_order(self, response: dict, base_market: str = "KRW") -> ModifyOrderResponse:
        self._raise_not_implemented_error()

    def parse_cancel_order(self, response: dict, base_market: str = "KRW") -> CancelOrderResponse:
        self._raise_not_implemented_error()

    def parse_create_order(self, response: dict, base_market: str = "KRW") -> CreateOrderResponse:
        self._raise_not_implemented_error()

    def parse_withdrawal_history(
        self, response: List[Dict], start: datetime | None = None, end: datetime | None = None, base_market: str = "KRW"
    ) -> WithdrawalHistory:
        self._raise_not_implemented_error()

    def parse_deposit_history(
        self, response: List[Dict], start: datetime | None = None, end: datetime | None = None, base_market: str = "KRW"
    ) -> DepositHistory:
        self._raise_not_implemented_error()

    def _parse_transaction_history_item(self, item: Dict, base_market: str = "KRW") -> TransactionInfo:
        self._raise_not_implemented_error()

    def parse_is_holiday(self, response: List[Dict], base_market: str = "KRW") -> HolidayHistory:
        self._raise_not_implemented_error()

    def _parse_is_holiday(self, item: Dict, base_market: str = "KRW") -> HolidayInfo:
        self._raise_not_implemented_error()
