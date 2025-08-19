import base64
import hashlib
import hmac
import json
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from urllib.parse import urlencode
import uuid

import jwt

from ksxt.api.bithumb import ImplicitAPI
from ksxt.async_.base.async_exchange import AsyncExchange
from ksxt.parser.bithumb import BithumbParser

import ksxt.models


class Bithumb(AsyncExchange, ImplicitAPI):
    def __init__(self, config: Dict = None):
        super().__init__(config, "bithumb.toml")
        self.parser = BithumbParser()

    def safe_symbol(self, base_market: str, security: str) -> str:
        # If security already contains a hyphen, assume it's correctly formatted
        if "-" in security:
            return security

        return f"{base_market}-{security}"

    def sign(
        self,
        path,
        security_type,
        method_type,
        api_type: Any = "public",
        headers: Optional[Any] = None,
        body: Optional[Any] = None,
        params: Optional[Any] = None,
        config={},
    ):
        host_url = self.apis[self.type]["hostname"]
        destination = self.apis[self.type][security_type][path]["url"]
        version = self.apis[self.type]["version"]
        destination = self.implode_params(destination, params)

        url = host_url + "/" + version + "/" + destination

        if api_type == "private":
            payload = {
                "access_key": self.open_key,
                "nonce": str(uuid.uuid4()),
                "timestamp": round(self.milliseconds()),
            }

            if params is not None and len(params) > 0:
                query = urlencode(params).encode()

                hash = hashlib.sha512()
                hash.update(query)
                query_hash = hash.hexdigest()

                payload.update({"query_hash": query_hash, "query_hash_alg": "SHA512"})

            jwt_token = jwt.encode(payload=payload, key=self.secret_key)
            authorization_token = f"Bearer {jwt_token}"

            if headers is None:
                headers = {}
                headers.update(
                    {"Content-Type": "application/json; charset=utf-8", "Authorization": authorization_token}
                )

        if method_type.upper() == "POST":
            body = json.dumps(params)
            params = {}

        return {"url": url, "method": method_type, "headers": headers, "body": body, "params": params}

    def get_common_response(self, response):
        if "error" in response:
            return self.create_common_response(
                success="1",
                msg_code=self.safe_string(response["error"], "name"),
                msg=self.safe_string(response["error"], "message"),
                info=response,
            )

        return self.create_common_response(
            success="0",
            msg_code=self.safe_string(response, "name"),
            msg=self.safe_string(response, "message"),
            info=response,
        )

    async def fetch_markets(self, market_name: str = "KRW") -> ksxt.models.KsxtMarketResponse:
        params = {
            # 유의종목 필드과 같은 상세 정보 노출 여부(선택 파라미터)
            "isDetails": "True"
        }

        common_header = self.create_common_header(request_params=params)

        response = await self.public_get_fetch_markets(self.extend(params))

        common_response = self.get_common_response(response=response)
        if common_response.success != "0":
            return ksxt.models.KsxtMarketResponse(header=common_header, response=common_response, info=None)

        parsed_info = self.parser.parse_markets(response=response, base_market=market_name)
        return ksxt.models.KsxtMarketResponse(header=common_header, response=common_response, info=parsed_info)

    async def fetch_historical_data(
        self,
        symbol: str,
        time_frame: str,
        start: datetime | None = None,
        end: datetime | None = None,
        base_market: str = "KRW",
    ) -> ksxt.models.KsxtHistoricalDataResponse:
        params = {"market": self.safe_symbol(base_market=base_market, security=symbol), "count": 200}

        if end:
            end_utc = end.astimezone(timezone.utc)
            params.update({"to": end_utc.strftime("%Y-%m-%d %H:%M:%S")})

        common_header = self.create_common_header(request_params=params)

        # TODO : time_frame 을 어떻게 고정시킬까? 우리는 분봉, 일봉, 주봉, 월봉 만 지원한다고 가정하면?
        if time_frame.endswith("m"):
            # TODO : parse number
            period = 1
            params.update({"unit": period})

            response = await self.public_get_fetch_security_ohlcv_minute(self.extend(params))

        elif time_frame.endswith("D"):
            response = await self.public_get_fetch_security_ohlcv_day(self.extend(params))

        elif time_frame.endswith("W"):
            response = await self.public_get_fetch_security_ohlcv_week(self.extend(params))

        elif time_frame.endswith("M"):
            response = await self.public_get_fetch_security_ohlcv_month(self.extend(params))

        common_response = self.get_common_response(response=response)
        if common_response.success != "0":
            return ksxt.models.KsxtHistoricalDataResponse(header=common_header, response=common_response, info=None)

        parsed_response = self.parser.parse_historical_data(
            response=response, symbol=symbol, start=start, end=end, base_market=base_market
        )

        return ksxt.models.KsxtHistoricalDataResponse(
            header=common_header, response=common_response, info=parsed_response
        )

    async def fetch_ticker(self, symbol: str, base_market: str = "KRW") -> ksxt.models.KsxtTickerResponse:
        params = {"markets": self.safe_symbol(base_market=base_market, security=symbol)}

        common_header = self.create_common_header(request_params=params)

        response = await self.public_get_fetch_ticker_price(self.extend(params))

        common_response = self.get_common_response(response=response)

        # 실패 시 오류 응답 반환
        if common_response.success != "0":
            return ksxt.models.KsxtTickerResponse(header=common_header, response=common_response, info=None)

        # 데이터 파싱
        parsed_info = self.parser.parse_ticker(response, base_market)

        return ksxt.models.KsxtTickerResponse(header=common_header, response=common_response, info=parsed_info)

    async def fetch_tickers(self, symbols: List[str], base_market: str = "KRW") -> ksxt.models.KsxtTickersResponse:
        symbol = ",".join([self.safe_symbol(base_market, symbol) for symbol in symbols])
        params = {"markets": symbol}

        common_header = self.create_common_header(request_params=params)

        response = await self.public_get_fetch_tickers_price(self.extend(params))

        common_response = self.get_common_response(response=response)

        # 실패 시 오류 응답 반환
        if common_response.success != "0":
            return ksxt.models.KsxtTickersResponse(header=common_header, response=common_response, info=None)

        # 데이터 파싱
        parsed_info = self.parser.parse_tickers(response, base_market)

        return ksxt.models.KsxtTickersResponse(header=common_header, response=common_response, info=parsed_info)

    async def fetch_orderbook(self, symbol: str, base_market: str = "KRW") -> ksxt.models.KsxtSingleOrderBookResponse:
        params = {"markets": self.safe_symbol(base_market, symbol)}

        common_header = self.create_common_header(request_params=params)

        response = await self.public_get_fetch_orderbook(self.extend(params))

        common_response = self.get_common_response(response=response)

        # 실패 시 오류 응답 반환
        if common_response.success != "0":
            return ksxt.models.KsxtSingleOrderBookResponse(header=common_header, response=common_response, info=None)

        # 데이터 파싱
        parsed_info = self.parser.parse_orderbook(response, base_market)

        return ksxt.models.KsxtSingleOrderBookResponse(header=common_header, response=common_response, info=parsed_info)

    async def fetch_orderbooks(
        self, symbols: List[str], base_market: str = "KRW"
    ) -> ksxt.models.KsxtMultiOrderBookResponse:
        symbol = ",".join([self.safe_symbol(base_market, symbol) for symbol in symbols])
        params = {
            #'markets': self.safe_symbol(base_market, symbol)
            "markets": symbol  # 이렇게 해야 정상동작!
        }

        common_header = self.create_common_header(request_params=params)

        response = await self.public_get_fetch_orderbooks(self.extend(params))

        common_response = self.get_common_response(response=response)

        # 실패 시 오류 응답 반환
        if common_response.success != "0":
            return ksxt.models.KsxtMultiOrderBookResponse(header=common_header, response=common_response, info=None)

        # 데이터 파싱
        parsed_info = self.parser.parse_orderbooks(response, base_market)

        return ksxt.models.KsxtMultiOrderBookResponse(header=common_header, response=common_response, info=parsed_info)

    async def fetch_balance(
        self,
        acc_num: str,
        base_market: str = "KRW",
        excluded_symbols: list[str] | None = None,
        included_symbols: list[str] | None = None,
        filter_delisted: bool = True,
        min_amount: float = 0,
    ) -> ksxt.models.KsxtBalanceResponse:
        params = {}

        common_header = self.create_common_header(request_params=params)

        response = await self.private_get_fetch_balance(self.extend(params))

        common_response = self.get_common_response(response=response)

        # 실패 시 오류 응답 반환
        if common_response.success != "0":
            return ksxt.models.KsxtBalanceResponse(header=common_header, response=common_response, info=None)

        # 데이터 파싱
        parsed_info = self.parser.parse_balance(
            response=response,
            base_market=base_market,
            excluded_symbols=excluded_symbols,
            included_symbols=included_symbols,
            filter_delisted=filter_delisted,
            min_amount=min_amount,
        )

        return ksxt.models.KsxtBalanceResponse(header=common_header, response=common_response, info=parsed_info)

    async def fetch_cash(self, acc_num: str, base_market: str = "KRW") -> ksxt.models.KsxtCashResponse:
        params = {}

        common_header = self.create_common_header(request_params=params)

        response = await self.private_get_fetch_cash(self.extend(params))

        common_response = self.get_common_response(response=response)

        # 실패 시 오류 응답 반환
        if common_response.success != "0":
            return ksxt.models.KsxtCashResponse(header=common_header, response=common_response, info=None)

        # 데이터 파싱
        parsed_info = self.parser.parse_cash(response, base_market)

        return ksxt.models.KsxtCashResponse(header=common_header, response=common_response, info=parsed_info)

    async def fetch_security(self, symbol: str, base_market: str = "KRW") -> ksxt.models.KsxtSecurityResponse:
        params = {"market": self.safe_symbol(base_market, symbol)}

        common_header = self.create_common_header(request_params=params)

        response = await self.public_get_fetch_security_info(self.extend(params))

        common_response = self.get_common_response(response=response)

        # 실패 시 오류 응답 반환
        if common_response.success != "0":
            return ksxt.models.KsxtSecurityResponse(header=common_header, response=common_response, info=None)

        # 데이터 파싱
        parsed_info = self.parser.parse_security(response, base_market)

        return ksxt.models.KsxtSecurityResponse(header=common_header, response=common_response, info=parsed_info)

    async def fetch_trade_fee(
        self, symbol: Optional[str] = "", base_market: str = "KRW"
    ) -> ksxt.models.KsxtTradeFeeResponse:
        params = {"market": self.safe_symbol(base_market, symbol)}

        common_header = self.create_common_header(request_params=params)

        response = await self.private_get_fetch_trade_fee(self.extend(params))

        common_response = self.get_common_response(response=response)
        if common_response.success != "0":
            return ksxt.models.KsxtTradeFeeResponse(header=common_header, response=common_response, info=None)

        parsed_info = self.parser.parse_trade_fee(response, base_market)
        return ksxt.models.KsxtTradeFeeResponse(header=common_header, response=common_response, info=parsed_info)

    async def fetch_open_order(
        self,
        acc_num: str,
        symbol: Optional[str] = "",
        start: datetime | None = None,
        end: datetime | None = None,
        base_market: str = "KRW",
    ) -> ksxt.models.KsxtOpenOrderResponse:
        params = {
            "market": self.safe_symbol(base_market, symbol),
            "uuids": "",
            #'state': 'wait'
        }

        common_header = self.create_common_header(request_params=params)

        response = await self.private_get_fetch_opened_order(self.extend(params))

        common_response = self.get_common_response(response=response)

        # 실패 시 오류 응답 반환
        if common_response.success != "0":
            return ksxt.models.KsxtOpenOrderResponse(header=common_header, response=common_response, info=None)

        # 데이터 파싱
        parsed_info = self.parser.parse_open_order_history(
            response=response, start=start, end=end, base_market=base_market
        )

        return ksxt.models.KsxtOpenOrderResponse(header=common_header, response=common_response, info=parsed_info)

    async def fetch_closed_order(
        self,
        acc_num: str,
        symbol: Optional[str] = "",
        start: datetime | None = None,
        end: datetime | None = None,
        base_market: str = "KRW",
    ) -> ksxt.models.KsxtClosedOrderResponse:
        params = {"market": self.safe_symbol(base_market, symbol), "uuids": "", "state": "done"}

        common_header = self.create_common_header(request_params=params)

        response = await self.private_get_fetch_closed_order(self.extend(params))

        common_response = self.get_common_response(response=response)

        # 실패 시 오류 응답 반환
        if common_response.success != "0":
            return ksxt.models.KsxtClosedOrderResponse(header=common_header, response=common_response, info=None)

        # 데이터 파싱
        parsed_info = self.parser.parse_closed_order_history(
            response=response, start=start, end=end, base_market=base_market
        )

        return ksxt.models.KsxtClosedOrderResponse(header=common_header, response=common_response, info=parsed_info)

    async def cancel_order(
        self, acc_num: str, order_id: str, symbol: str | None = "", qty: float = 0, base_market: str = "KRW", **kwargs
    ) -> ksxt.models.KsxtCancelOrderResponse:
        params = {"uuid": order_id}

        common_header = self.create_common_header(request_params=params)

        response = await self.private_delete_send_cancel_order(self.extend(params))

        common_response = self.get_common_response(response=response)

        # 실패 시 오류 응답 반환
        if common_response.success != "0":
            return ksxt.models.KsxtCancelOrderResponse(header=common_header, response=common_response, info=None)

        # 데이터 파싱
        parsed_info = self.parser.parse_cancel_order(response, base_market)

        return ksxt.models.KsxtCancelOrderResponse(header=common_header, response=common_response, info=parsed_info)

    async def create_order(
        self,
        acc_num: str,
        symbol: str,
        ticket_type: Literal["EntryLong", "EntryShort", "ExitLong", "ExitShort"],
        otype: Literal["limit", "market"],
        price: Optional[float] = 0,
        qty: Optional[float] = 0,
        amount: Optional[float] = 0,
        base_market: str = "KRW",
    ) -> ksxt.models.KsxtCreateOrderResponse:
        params = {
            "market": self.safe_symbol(base_market, symbol),
        }

        if ticket_type == "EntryLong":
            order_side = "bid"
            if otype == "limit":
                params.update({"side": order_side, "volume": qty, "price": price, "ord_type": "limit"})
                response = await self.private_post_send_order_entry(self.extend(params))

            elif otype == "market":
                params.update({"side": order_side, "price": amount, "ord_type": "price"})
                response = await self.private_post_send_order_entry_market(self.extend(params))

        elif ticket_type == "ExitLong":
            order_side = "ask"
            if otype == "limit":
                params.update({"side": order_side, "volume": qty, "price": price, "ord_type": "limit"})
                response = await self.private_post_send_order_exit(self.extend(params))

            elif otype == "market":
                params.update({"side": order_side, "volume": qty, "ord_type": "market"})
                response = await self.private_post_send_order_exit_market(self.extend(params))

        common_header = self.create_common_header(request_params=params)
        common_response = self.get_common_response(response=response)

        # 실패 시 오류 응답 반환
        if common_response.success != "0":
            return ksxt.models.KsxtCreateOrderResponse(header=common_header, response=common_response, info=None)

        # 데이터 파싱
        parsed_info = self.parser.parse_create_order(response, base_market)

        return ksxt.models.KsxtCreateOrderResponse(header=common_header, response=common_response, info=parsed_info)

    async def fetch_withdrawal_history(
        self, acc_num: str, start: datetime | None = None, end: datetime | None = None, base_market: str = "KRW"
    ) -> ksxt.models.KsxtWithdrawalHistoryResponse:
        params = {"state": "DONE", "uuids": "", "txids": ""}

        common_header = self.create_common_header(request_params=params)

        response = await self.private_get_fetch_withdrawal_history(self.extend(params))

        common_response = self.get_common_response(response=response)

        # 실패 시 오류 응답 반환
        if common_response.success != "0":
            return ksxt.models.KsxtWithdrawalHistoryResponse(header=common_header, response=common_response, info=None)

        # 데이터 파싱
        parsed_info = self.parser.parse_withdrawal_history(
            response=response, start=start, end=end, base_market=base_market
        )

        return ksxt.models.KsxtWithdrawalHistoryResponse(
            header=common_header, response=common_response, info=parsed_info
        )

    async def fetch_deposit_history(
        self, acc_num: str, start: datetime | None = None, end: datetime | None = None, base_market: str = "KRW"
    ) -> ksxt.models.KsxtDepositHistoryResponse:
        params = {"state": "ACCEPTED", "uuids": "", "txids": ""}

        common_header = self.create_common_header(request_params=params)

        response = await self.private_get_fetch_deposit_history(self.extend(params))

        common_response = self.get_common_response(response=response)

        # 실패 시 오류 응답 반환
        if common_response.success != "0":
            return ksxt.models.KsxtDepositHistoryResponse(header=common_header, response=common_response, info=None)

        # 데이터 파싱
        parsed_info = self.parser.parse_deposit_history(
            response=response, start=start, end=end, base_market=base_market
        )

        return ksxt.models.KsxtDepositHistoryResponse(header=common_header, response=common_response, info=parsed_info)
