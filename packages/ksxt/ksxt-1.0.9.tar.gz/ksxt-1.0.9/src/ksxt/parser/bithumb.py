from datetime import datetime, timezone
from typing import Dict, List, Optional

from ksxt.models.transaction import (
    ClosedOrderHistory,
    DepositHistory,
    OpenedOrderHistory,
    TransactionInfo,
    WithdrawalHistory,
)
from ksxt.models.balance import BalanceData, BalanceInfo
from ksxt.models.cash import CashInfo
from ksxt.models.historical import HistoricalDataInfo, OHLCVData
from ksxt.models.market import MarketInfo, SecurityData, TradeFeeInfo
from ksxt.models.order import CancelOrderResponse, CreateOrderResponse
from ksxt.models.orderbook import MultiSymbolOrderBookInfos, OrderBookData, OrderBookInfo
from ksxt.models.ticker import MultiSymbolTickerInfo, TickerInfo
from ksxt.parser.parser import BaseParser
from ksxt.utils import safer, sorter


class BithumbParser(BaseParser):
    def safe_symbol(self, base_market: str, security: str) -> str:
        # If security already contains a hyphen, assume it's correctly formatted
        if "-" in security:
            return security

        return f"{base_market}-{security}"

    def parse_markets(self, response: List[Dict], base_market: str = "KRW") -> MarketInfo:
        securities = {}
        for market in response:
            market_base = market["market"].split("-")[0]
            if market_base != base_market:
                continue

            security_data = self._parse_market(market)
            securities[security_data.symbol] = security_data

        return MarketInfo(market_id=base_market, securities=securities)

    def _parse_market(self, market: Dict) -> SecurityData:
        return SecurityData(
            symbol=safer.safe_string(market, "market"),
            name=safer.safe_string(market, "korean_name"),
            type="crypto",
            warning_code=False if safer.safe_string(market, "market_warning") == "NONE" else True,
        )

    def parse_historical_data(
        self,
        response: List[Dict],
        symbol: str,
        start: datetime | None = None,
        end: datetime | None = None,
        base_market: str = "KRW",
    ) -> HistoricalDataInfo:
        ohlcv = [self._parse_ohlcva(_, base_market) for _ in response]

        # Filter by start and end datetime
        if start:
            ohlcv = [data for data in ohlcv if data.datetime >= start]
        if end:
            ohlcv = [data for data in ohlcv if data.datetime <= end]

        sorted_ohlcv = sorter.sort_by(ohlcv, key="datetime")

        security_name = symbol

        result = HistoricalDataInfo(
            symbol=self.safe_symbol(base_market, security_name), security_name=security_name, history=sorted_ohlcv
        )

        return result

    def _parse_ohlcva(self, ohlcva: dict, base_market: str = "KRW") -> OHLCVData:
        fmt = "%Y-%m-%dT%H:%M:%S"
        return OHLCVData(
            datetime=datetime.strptime(safer.safe_string(ohlcva, "candle_date_time_kst"), fmt),
            open_price=safer.safe_number(ohlcva, "opening_price"),
            high_price=safer.safe_number(ohlcva, "high_price"),
            low_price=safer.safe_number(ohlcva, "low_price"),
            close_price=safer.safe_number(ohlcva, "trade_price"),
            acml_volume=safer.safe_number(ohlcva, "candle_acc_trade_volume"),
            acml_amount=safer.safe_number(ohlcva, "candle_acc_trade_price"),
        )

    def parse_ticker(self, response: List[Dict], base_market: str = "KRW") -> TickerInfo:
        ticker_info = self._parse_ticker(response[0], base_market=base_market)
        return ticker_info

    def parse_tickers(self, response: List[Dict], base_market: str = "KRW") -> MultiSymbolTickerInfo:
        tickers_info = {}

        for ticker_data in response:
            symbol = safer.safe_string(ticker_data, "market")
            ticker_info = self._parse_ticker(ticker_data, base_market)
            tickers_info[symbol] = ticker_info

        return MultiSymbolTickerInfo(tickers=tickers_info)

    def _parse_ticker(self, response: dict, base_market: str) -> TickerInfo:
        timestamp_ms = safer.safe_number(response, "timestamp")
        timestamp_s = timestamp_ms / 1000.0

        return TickerInfo(
            symbol=safer.safe_string(response, "market"),
            price=safer.safe_number(response, "trade_price"),
            ts=datetime.fromtimestamp(timestamp_s),
        )

    def parse_orderbook(self, response: List[Dict], base_market: str = "KRW") -> OrderBookInfo:
        ask_list = []
        bid_list = []

        for item in response:
            for index, data in enumerate(item["orderbook_units"]):
                ask_data, bid_data = self._parse_orderbook(data, index, base_market)
                ask_list.append(ask_data)
                bid_list.append(bid_data)

        return OrderBookInfo(
            total_asks_qty=safer.safe_string(response[0], "total_ask_size"),
            total_bids_qty=safer.safe_string(response[0], "total_bid_size"),
            asks=ask_list,
            bids=bid_list,
        )

    def parse_orderbooks(self, response: dict, base_market: str) -> MultiSymbolOrderBookInfos:
        order_books = {}

        # response에서 'order_books' 항목이 리스트 형태로 되어 있다고 가정
        for symbol_info in response:
            symbol = symbol_info["market"]  # 각 종목의 심볼 추출
            orderbook_units = symbol_info["orderbook_units"]  # 호가 정보 추출

            ask_list = []
            bid_list = []

            for index, data in enumerate(orderbook_units):
                ask_data, bid_data = self._parse_orderbook(data, index, base_market)
                ask_list.append(ask_data)
                bid_list.append(bid_data)

            # OrderBookInfo 객체 생성
            order_book_info = OrderBookInfo(
                total_asks_qty=safer.safe_number(symbol_info, "total_ask_size"),
                total_bids_qty=safer.safe_number(symbol_info, "total_bid_size"),
                asks=ask_list,
                bids=bid_list,
            )

            # 심볼과 함께 OrderBookInfo를 딕셔너리에 추가
            order_books[symbol] = order_book_info

        # MultiSymbolOrderBookInfo 객체 반환
        return MultiSymbolOrderBookInfos(order_books=order_books)

    def _parse_orderbook(
        self, orderbook: dict, index: int, base_market: str = "KRW"
    ) -> tuple[OrderBookData, OrderBookData]:
        ask_data = OrderBookData(
            side="ask",
            ob_num=index,
            ob_price=safer.safe_number(orderbook, "ask_price"),
            ob_qty=safer.safe_number(orderbook, "ask_size"),
        )

        bid_data = OrderBookData(
            side="bid",
            ob_num=index,
            ob_price=safer.safe_number(orderbook, "bid_price"),
            ob_qty=safer.safe_number(orderbook, "bid_size"),
        )

        return ask_data, bid_data

    def parse_balance(
        self,
        response: List[Dict],
        base_market: str = "KRW",
        excluded_symbols: Optional[list[str]] = None,
        included_symbols: Optional[list[str]] = None,
        filter_delisted: bool = True,
        min_amount: float = 0,
    ) -> BalanceInfo:
        # 1. Filter out entries where 'currency' is not the base_market
        # 2. Ensure 'unit_currency' is the base_market
        # 3. Exclude entries where 'currency' is in excluded_symbols
        filtered_data = [
            data
            for data in response
            if data["currency"] != base_market
            and data["unit_currency"] == base_market
            and (excluded_symbols is None or data["currency"] not in excluded_symbols)
            and (included_symbols is None or self.safe_symbol(base_market, data["currency"]) in included_symbols)
        ]

        # Initialize balance list
        balances = [self._parse_balance(data, base_market) for data in filtered_data]

        if filter_delisted:
            balances = [balance for balance in balances if balance.price > 0]

        if min_amount > 0:
            balances = [balance for balance in balances if balance.amount > min_amount]

        # 총 매입금액
        total_amount = sum(bal.price * bal.qty for bal in balances)
        total_evaluation_amount = sum(bal.evaluation_price * bal.qty for bal in balances)
        total_pnl_amount = total_evaluation_amount - total_amount
        total_pnl_ratio = (total_pnl_amount / total_amount * 100) if total_amount != 0 else 0

        return BalanceInfo(
            currency=base_market,
            total_amount=total_amount,
            total_evaluation_amount=total_amount,
            total_pnl_amount=total_pnl_amount,
            total_pnl_ratio=total_pnl_ratio,
            balances=balances,
        )

    def _parse_balance(self, data: Dict, base_market: str = "KRW") -> BalanceData:
        return BalanceData(
            symbol=self.safe_symbol(base_market, safer.safe_string(data, "currency")),
            name=self.safe_symbol(base_market, safer.safe_string(data, "currency")),
            evaluation_price=0,  # 필요에 따라 적절히 설정
            price=safer.safe_number(data, "avg_buy_price"),
            qty=safer.safe_number(data, "balance"),
            free_qty=safer.safe_number(data, "balance") - safer.safe_number(data, "locked"),
            used_qty=safer.safe_number(data, "locked"),
        )

    def parse_cash(self, response: List[Dict], base_market: str = "KRW") -> CashInfo:
        # 1. Filter entries where 'currency' is equal to 'base_market'
        # 2. Ensure 'unit_currency' is also equal to 'base_market'
        filtered_data = [
            data for data in response if data["currency"] == base_market and data["unit_currency"] == base_market
        ]

        # 필터링된 데이터가 없으면 기본값으로 CashInfo 반환
        if not filtered_data:
            return CashInfo(currency=base_market, cash=0.0, cash_d1=0.0, cash_d2=0.0)

        # 필터링된 첫 번째 항목을 가져와서 CashInfo 생성
        data = filtered_data[0]

        return CashInfo(
            currency=base_market,
            cash=safer.safe_number(data, "balance"),
            cash_d1=safer.safe_number(data, "balance"),  # 데이터를 가정하여 같은 값 사용
            cash_d2=safer.safe_number(data, "balance"),  # 데이터를 가정하여 같은 값 사용
        )

    def parse_security(self, response: dict, base_market: str = "KRW") -> SecurityData:
        market_info = response.get("market", {})

        return SecurityData(
            symbol=safer.safe_string(market_info, "id"),
            name=safer.safe_string(market_info, "name"),
            type="crypto",
            bid_qty_unit=safer.safe_number(market_info["bid"], "price_unit"),
            ask_qty_unit=safer.safe_number(market_info["ask"], "price_unit"),
            bid_min_qty=0,
            ask_min_qty=0,
            bid_max_qty=0,
            ask_max_qty=0,
            bid_amount_unit=1,
            ask_amount_unit=1,
            bid_min_amount=safer.safe_number(market_info["bid"], "min_total"),
            ask_min_amount=safer.safe_number(market_info["ask"], "min_total"),
            bid_max_amount=safer.safe_number(market_info, "max_total"),
            ask_max_amount=safer.safe_number(market_info, "max_total"),
            warning_code=safer.safe_string(market_info, "state") != "active",
        )

    def parse_trade_fee(self, response: dict, base_market: str = "KRW") -> TradeFeeInfo:
        return TradeFeeInfo(
            limit_bid_fee=safer.safe_number(response, "bid_fee"),
            limit_ask_fee=safer.safe_number(response, "ask_fee"),
            market_bid_fee=safer.safe_number(response, "maker_bid_fee"),
            market_ask_fee=safer.safe_number(response, "maker_ask_fee"),
        )

    def parse_open_order_history(
        self, response: List[Dict], start: datetime | None = None, end: datetime | None = None, base_market: str = "KRW"
    ) -> OpenedOrderHistory:
        orders = [self._parse_open_order_info(order, base_market) for order in response]

        # Filter by start and end datetime
        if start:
            orders = [
                order for order in orders if order.created_at.astimezone(timezone.utc) >= start.astimezone(timezone.utc)
            ]
        if end:
            orders = [
                order for order in orders if order.created_at.astimezone(timezone.utc) <= end.astimezone(timezone.utc)
            ]

        return OpenedOrderHistory(history=orders)

    def _parse_open_order_info(self, order: dict, base_market: str = "KRW") -> TransactionInfo:
        return TransactionInfo(
            uuid=safer.safe_string(order, "uuid"),
            account_id="",
            transaction_type=safer.safe_string(order, "side"),
            order_type=safer.safe_string(order, "ord_type"),
            tr_position="long",
            symbol=self.safe_symbol(base_market, safer.safe_string(order, "market")),
            price=safer.safe_number(order, "price"),
            qty=safer.safe_number(order, "volume"),
            amount=safer.safe_number(order, "price") * safer.safe_number(order, "volume"),
            tax=0,
            fee=safer.safe_number(order, "reserved_fee"),
            currency=base_market,
            created_at=datetime.fromisoformat(safer.safe_string(order, "created_at")),
        )

    def parse_closed_order_history(
        self, response: List[Dict], start: datetime | None = None, end: datetime | None = None, base_market: str = "KRW"
    ) -> ClosedOrderHistory:
        orders = [self._parse_closed_order_info(order, base_market) for order in response]

        # Filter by start and end datetime
        if start:
            orders = [
                order for order in orders if order.created_at.astimezone(timezone.utc) >= start.astimezone(timezone.utc)
            ]
        if end:
            orders = [
                order for order in orders if order.created_at.astimezone(timezone.utc) <= end.astimezone(timezone.utc)
            ]

        return ClosedOrderHistory(history=orders)

    def _parse_closed_order_info(self, order: dict, base_market: str = "KRW") -> TransactionInfo:
        return TransactionInfo(
            uuid=safer.safe_string(order, "uuid"),
            account_id="",
            transaction_type=safer.safe_string(order, "side"),
            order_type=safer.safe_string(order, "ord_type"),
            tr_position="long",
            symbol=self.safe_symbol(base_market, safer.safe_string(order, "market")),
            price=safer.safe_number(order, "price"),
            qty=safer.safe_number(order, "volume"),
            amount=safer.safe_number(order, "price") * safer.safe_number(order, "volume"),
            tax=0,
            fee=safer.safe_number(order, "reserved_fee"),
            currency=base_market,
            created_at=datetime.fromisoformat(safer.safe_string(order, "created_at")),
        )

    def parse_cancel_order(self, response: dict, base_market: str = "KRW") -> CancelOrderResponse:
        return CancelOrderResponse(order_datetime=datetime.now(), order_id=safer.safe_string(response, "uuid"))

    def parse_create_order(self, response: dict, base_market: str = "KRW") -> CreateOrderResponse:
        return CreateOrderResponse(order_datetime=datetime.now(), order_id=safer.safe_string(response, "uuid"))

    def parse_withdrawal_history(
        self, response: List[Dict], start: datetime | None = None, end: datetime | None = None, base_market: str = "KRW"
    ) -> WithdrawalHistory:
        parsed_items = [self._parse_transaction_history_item(item, base_market) for item in response]

        # Filter by start and end datetime
        if start:
            parsed_items = [
                item
                for item in parsed_items
                if item.created_at.astimezone(timezone.utc) >= start.astimezone(timezone.utc)
            ]
        if end:
            parsed_items = [
                item
                for item in parsed_items
                if item.created_at.astimezone(timezone.utc) <= end.astimezone(timezone.utc)
            ]

        return WithdrawalHistory(history=parsed_items)

    def parse_deposit_history(
        self, response: List[Dict], start: datetime | None = None, end: datetime | None = None, base_market: str = "KRW"
    ) -> DepositHistory:
        parsed_items = [self._parse_transaction_history_item(item, base_market) for item in response]

        # Filter by start and end datetime
        if start:
            parsed_items = [
                item
                for item in parsed_items
                if item.created_at.astimezone(timezone.utc) >= start.astimezone(timezone.utc)
            ]
        if end:
            parsed_items = [
                item
                for item in parsed_items
                if item.created_at.astimezone(timezone.utc) <= end.astimezone(timezone.utc)
            ]

        return DepositHistory(history=parsed_items)

    def _parse_transaction_history_item(self, item: Dict, base_market: str = "KRW") -> TransactionInfo:
        return TransactionInfo(
            uuid=safer.safe_string(item, "uuid"),
            account_id="",
            transaction_type=safer.safe_string(item, "type"),
            order_type=safer.safe_string(item, "transaction_type"),
            tr_position="",
            symbol=safer.safe_string(item, "currency"),
            price=1,
            qty=safer.safe_number(item, "amount"),
            amount=safer.safe_number(item, "amount"),
            tax=0,
            fee=safer.safe_number(item, "fee"),
            currency=safer.safe_string(item, "currency"),
            created_at=datetime.fromisoformat(safer.safe_string(item, "done_at")),
        )
