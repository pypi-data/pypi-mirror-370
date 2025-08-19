from datetime import datetime
from typing import Dict, List, Optional

from ksxt.models.balance import BalanceData, BalanceInfo
from ksxt.models.cash import CashInfo
from ksxt.models.historical import HistoricalDataInfo, OHLCVData
from ksxt.models.market import HolidayHistory, HolidayInfo, MarketInfo, SecurityData, TradeFeeInfo
from ksxt.models.order import CancelOrderResponse, CreateOrderResponse, ModifyOrderResponse
from ksxt.models.orderbook import OrderBookData, OrderBookInfo
from ksxt.models.ticker import MultiSymbolTickerInfo, TickerInfo
from ksxt.models.token import TokenInfo
from ksxt.models.transaction import (
    ClosedOrderHistory,
    DepositHistory,
    OpenedOrderHistory,
    TransactionInfo,
)
from ksxt.parser.parser import BaseParser
from ksxt.utils import safer, sorter, timer


class KoreaInvestParser(BaseParser):
    def safe_symbol(self, base_market: str, symbol: str) -> str:
        return symbol

    def parse_token(self, response: dict) -> TokenInfo:
        date_string = safer.safe_string(response, "access_token_token_expired")
        date_format = "%Y-%m-%d %H:%M:%S"
        expired_date = datetime.strptime(date_string, date_format)

        return TokenInfo(
            access_token=safer.safe_string(response, "access_token"),
            token_type=safer.safe_string(response, "token_type"),
            remain_time_second=safer.safe_number(response, "expires_in"),
            expired_datetime=expired_date,
        )

    def parse_markets(self, response: dict, base_market: str = "KRW") -> MarketInfo:
        securities = {}
        for market in response:
            security_data = self._parse_market(market, base_market)
            securities[security_data.symbol] = security_data

        return MarketInfo(market_id=base_market, securities=securities)

    def _parse_market(self, market: Dict, base_market: str = "KRW") -> SecurityData:
        return SecurityData(
            symbol=safer.safe_string(market, "market"),
            name=safer.safe_string(market, "korean_name"),
            type="stock",
            warning_code=safer.safe_boolean(market, " market_warning"),
        )

    def parse_historical_data(
        self,
        response: List[Dict],
        symbol: str,
        start: datetime | None = None,
        end: datetime | None = None,
        base_market: str = "KRW",
    ) -> HistoricalDataInfo:
        safe_response = safer.safe_value(response, "output2")
        ohlcv = [self._parse_ohlcva(_, base_market) for _ in safe_response]

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

    def _parse_ohlcva(self, ohlcva: Dict, base_market: str = "KRW") -> OHLCVData:
        fmt = "%Y%m%d"
        return OHLCVData(
            datetime=datetime.strptime(safer.safe_string(ohlcva, "stck_bsop_date"), fmt),
            open_price=safer.safe_number(ohlcva, "stck_oprc"),
            high_price=safer.safe_number(ohlcva, "stck_hgpr"),
            low_price=safer.safe_number(ohlcva, "stck_lwpr"),
            close_price=safer.safe_number(ohlcva, "stck_clpr"),
            acml_volume=safer.safe_number(ohlcva, "acml_vol"),
            acml_amount=safer.safe_number(ohlcva, "acml_tr_pbmn"),
        )

    def parse_historical_index_data(
        self,
        response: Dict,
        symbol: str,
        start: datetime | None = None,
        end: datetime | None = None,
        base_market: str = "KRW",
    ) -> HistoricalDataInfo:
        safe_response = safer.safe_value(response, "output2")
        ohlcv = [self._parse_index_ohlcva(_, base_market) for _ in safe_response]

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

    def _parse_index_ohlcva(self, ohlcva: Dict, base_market: str = "KRW") -> OHLCVData:
        fmt = "%Y%m%d"
        return OHLCVData(
            datetime=datetime.strptime(safer.safe_string(ohlcva, "stck_bsop_date"), fmt),
            open_price=safer.safe_number(ohlcva, "bstp_nmix_oprc"),
            high_price=safer.safe_number(ohlcva, "bstp_nmix_hgpr"),
            low_price=safer.safe_number(ohlcva, "bstp_nmix_lwpr"),
            close_price=safer.safe_number(ohlcva, "bstp_nmix_prpr"),
            acml_volume=safer.safe_number(ohlcva, "acml_vol"),
            acml_amount=safer.safe_number(ohlcva, "acml_tr_pbmn"),
        )

    def parse_ticker(self, response: List[Dict], base_market: str = "KRW") -> TickerInfo:
        safe_response = safer.safe_value(response, "output")
        ticker_info = self._parse_ticker(safe_response, base_market)
        return ticker_info

    def _parse_ticker(self, response: dict, base_market: str) -> TickerInfo:
        return TickerInfo(
            symbol=safer.safe_string(response, "stck_shrn_iscd"),
            price=safer.safe_number(response, "stck_prpr"),
            ts=datetime.now(),
        )

    def parse_orderbook(self, response: List[Dict], base_market: str = "KRW") -> OrderBookInfo:
        ask_list = []
        bid_list = []

        level = 10

        safe_response = safer.safe_value(response, "output1")

        for index in range(1, level + 1):
            ask_data, bid_data = self._parse_orderbook(safe_response, index, base_market)
            ask_list.append(ask_data)
            bid_list.append(bid_data)

        return OrderBookInfo(
            total_asks_qty=safer.safe_number(safe_response, "total_askp_rsqn"),
            total_bids_qty=safer.safe_number(safe_response, "total_askp_rsqn"),
            asks=ask_list,
            bids=bid_list,
        )

    def _parse_orderbook(
        self, orderbook: Dict, index: int, base_market: str = "KRW"
    ) -> tuple[OrderBookData, OrderBookData]:
        ask_data = OrderBookData(
            side="ask",
            ob_num=index,
            ob_price=safer.safe_number(orderbook, f"askp{index}"),
            ob_qty=safer.safe_number(orderbook, f"askp_rsqn{index}"),
        )

        bid_data = OrderBookData(
            side="bid",
            ob_num=index,
            ob_price=safer.safe_number(orderbook, f"bidp{index}"),
            ob_qty=safer.safe_number(orderbook, f"bidp_rsqn{index}"),
        )

        return ask_data, bid_data

    def parse_balance(
        self,
        response: List[Dict],
        base_market: str = "KRW",
        excluded_symbols: Optional[list[str]] = None,
        included_symbols: list[str] | None = None,
        filter_delisted: bool = True,
        min_amount: float = 0,
    ) -> BalanceInfo:
        safe_response = safer.safe_value(response, "output1")

        # Initialize balance list with filtering
        balances = [
            self._parse_balance(_, base_market)
            for _ in safe_response
            if (excluded_symbols is None or safer.safe_string(_, "pdno") not in excluded_symbols)
            and (included_symbols is None or safer.safe_string(_, "pdno") in included_symbols)
        ]

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
            total_evaluation_amount=total_evaluation_amount,
            total_pnl_amount=total_pnl_amount,
            total_pnl_ratio=total_pnl_ratio,
            balances=balances,
        )

    def _parse_balance(self, data: Dict, base_market: str = "KRW") -> BalanceData:
        return BalanceData(
            symbol=safer.safe_string(data, "pdno"),
            name=safer.safe_string(data, "prdt_name"),
            evaluation_price=safer.safe_number(data, "evlu_amt"),
            price=safer.safe_number(data, "pchs_avg_pric"),
            pnl=safer.safe_number(data, "evlu_pfls_amt"),
            pnl_ratio=safer.safe_number(data, "evlu_pfls_rt"),
            qty=safer.safe_number(data, "hldg_qty"),
            free_qty=safer.safe_number(data, "ord_psbl_qty"),
            used_qty=safer.safe_number(data, "hldg_qty") - safer.safe_number(data, "ord_psbl_qty"),
        )

    def parse_cash(self, response: List[Dict], base_market: str = "KRW") -> CashInfo:
        safe_response = safer.safe_value(response, "output2")

        return CashInfo(
            currency=base_market,
            cash=safer.safe_number(safe_response, "dnca_tot_amt"),
            cash_d1=safer.safe_number(safe_response, "nxdy_excc_amt"),
            cash_d2=safer.safe_number(safe_response, "prvs_rcdl_excc_amt"),
        )

    def parse_security(self, response: Dict, base_market: str = "KRW") -> SecurityData:
        safe_response = safer.safe_value(response, "output")

        return SecurityData(
            symbol=safer.safe_string(safe_response, "pdno")[-6:],
            name=safer.safe_string(safe_response, "prdt_name"),
            type=safer.safe_string(safe_response, "mket_id_cd"),
            bid_qty_unit=0,  # TODO : where is information?
            ask_qty_unit=0,  # TODO : where is information?
            bid_min_qty=0,  # TODO : where is information?
            ask_min_qty=0,  # TODO : where is information?
            bid_max_qty=0,  # TODO : where is information?
            ask_max_qty=0,  # TODO : where is information?
            bid_amount_unit=1,  # TODO: where is information?
            ask_amount_unit=1,  # TODO : where is information?
            bid_min_amount=0,  # TODO : where is information?
            ask_min_amount=0,  # TODO : where is information?
            bid_max_amount=0,  # TODO : where is information?
            ask_max_amount=0,  # TODO : where is information?
            # 거래정지여부 or 관리종목여부
            warning_code=safer.safe_string(safe_response, "tr_stop_yn") == "Y"
            or safer.safe_string(safe_response, "admn_item_yn") == "Y",
        )

    def parse_trade_fee(self, response: Dict, base_market: str = "KRW") -> TradeFeeInfo:
        # API에서 조회되는 내역을 찾지 못해 홈페이지 안내 문을 작성함. (단위 : %)
        # https://securities.koreainvestment.com/main/customer/guide/_static/TF04ae010000.jsp

        # 거래수수료
        trading_fee = 0.18

        # 매매수수료
        return TradeFeeInfo(
            limit_bid_fee=0.0140527 + trading_fee,
            limit_ask_fee=0.0140527 + trading_fee,
            market_bid_fee=0.0140527 + trading_fee,
            market_ask_fee=0.0140527 + trading_fee,
        )

    def parse_closed_order_history(
        self, response: List[Dict], start: datetime | None = None, end: datetime | None = None, base_market: str = "KRW"
    ) -> ClosedOrderHistory:
        safe_response = safer.safe_value(response, "output1")
        orders = [self._parse_closed_order_info(_, base_market) for _ in safe_response]

        # Filter by start and end datetime
        if start:
            orders = [order for order in orders if order.created_at >= start]
        if end:
            orders = [order for order in orders if order.created_at <= end]

        return ClosedOrderHistory(history=orders)

    def _parse_closed_order_info(self, order: Dict, base_market: str = "KRW") -> TransactionInfo:
        if safer.safe_string(order, "sll_buy_dvsn_cd") == "01":
            _type = "ask"
        else:
            _type = "bid"

        return TransactionInfo(
            uuid=safer.safe_string(order, "odno"),
            account_id="",
            # account_id=f'{safer.safe_string(order, "CANO")}-{safer.safe_string(order, "ACNT_PRDT_CD")}',
            transaction_type=_type,
            symbol=safer.safe_string(order, "pdno"),
            price=safer.safe_number(order, "avg_prvs"),
            qty=safer.safe_number(order, "tot_ccld_qty"),
            amount=safer.safe_number(order, "tot_ccld_amt"),
            tax=0,
            # 단일 주문 이력에는 수수료 관련 정보가 없고, 조회한 전체 목록에 대해 수수료 정보만 존재한다.
            fee=0,
            order_type=safer.safe_string(order, "avg_prvs"),
            created_at=datetime.fromisoformat(safer.safe_string(order, "ord_dt")),
        )

    def parse_open_order_history(
        self, response: List[Dict], start: datetime | None = None, end: datetime | None = None, base_market: str = "KRW"
    ) -> OpenedOrderHistory:
        safe_response = safer.safe_value(response, "output1")
        orders = [self._parse_open_order_info(_, base_market) for _ in safe_response]

        # Filter by start and end datetime
        if start:
            orders = [order for order in orders if order.created_at >= start]
        if end:
            orders = [order for order in orders if order.created_at <= end]

        return OpenedOrderHistory(history=orders)

    def _parse_open_order_info(self, order: Dict, base_market: str = "KRW") -> TransactionInfo:
        if safer.safe_string(order, "sll_buy_dvsn_cd") == "01":
            _type = "ask"
        else:
            _type = "bid"

        return TransactionInfo(
            uuid=safer.safe_string(order, "odno"),
            transaction_type=_type,
            symbol=safer.safe_string(order, "pdno"),
            price=safer.safe_number(order, "avg_prvs"),
            qty=safer.safe_number(order, "tot_ccld_qty"),
            amount=safer.safe_number(order, "tot_ccld_amt"),
            tax=0,
            # 단일 주문 이력에는 수수료 관련 정보가 없고, 조회한 전체 목록에 대해 수수료 정보만 존재한다.
            fee=0,
            currency=base_market,
            order_type=safer.safe_string(order, "avg_prvs"),
            created_at=datetime.fromisoformat(safer.safe_string(order, "ord_dt")),
        )

    def parse_create_order(self, response: Dict, base_market: str = "KRW") -> CreateOrderResponse:
        safe_response = safer.safe_value(response, "output")
        fmt = "%Y%m%d"

        order_hhmmss = datetime.strptime(safer.safe_string(safe_response, "ORD_TMD"), fmt)
        order_datetime = timer.create_datetime_with_today(order_hhmmss)

        return CreateOrderResponse(order_datetime=order_datetime, order_id=safer.safe_string(safe_response, "ODNO"))

    def parse_cancel_order(self, response: Dict, base_market: str = "KRW") -> CancelOrderResponse:
        safe_response = safer.safe_value(response, "output")
        fmt = "%Y%m%d"

        order_hhmmss = datetime.strptime(safer.safe_string(safe_response, "ORD_TMD"), fmt)
        order_datetime = timer.create_datetime_with_today(order_hhmmss)

        return CancelOrderResponse(order_datetime=order_datetime, order_id=safer.safe_string(safe_response, "ODNO"))

    def parse_modify_order(self, response: Dict, base_market: str = "KRW") -> ModifyOrderResponse:
        safe_response = safer.safe_value(response, "output")
        fmt = "%Y%m%d"

        order_hhmmss = datetime.strptime(safer.safe_string(safe_response, "ORD_TMD"), fmt)
        order_datetime = timer.create_datetime_with_today(order_hhmmss)

        return ModifyOrderResponse(order_datetime=order_datetime, order_id=safer.safe_string(safe_response, "ODNO"))

    def parse_is_holiday(self, response: List[Dict], base_market: str = "KRW") -> HolidayHistory:
        safe_response = safer.safe_value(response, "output")
        history = [self._parse_is_holiday(_, base_market) for _ in safe_response]

        return HolidayHistory(market=["kospi", "kosdaq"], country="KR", history=history)

    def _parse_is_holiday(self, item: Dict, base_market: str = "KRW") -> HolidayInfo:
        return HolidayInfo(
            date=datetime.strptime(safer.safe_string(item, "bass_dt"), "%Y%m%d"),
            weekend=safer.safe_string(item, "wday_dvsn_cd"),
            is_holiday=not safer.safe_boolean(item, "opnd_yn"),
        )
