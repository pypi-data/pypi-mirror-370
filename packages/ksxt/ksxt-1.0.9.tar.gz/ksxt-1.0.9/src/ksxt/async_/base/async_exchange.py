import logging
import asyncio
import toml
import os
import aiofiles
import time
import aiohttp
from datetime import datetime
from typing import Any, Dict, Literal, Optional


from ksxt.base.errors import NotSupportedError
from ksxt.base.rate_limiter import RateLimiterContext
from ksxt.base.rest_exchange import RestExchange
from ksxt.config import CONFIG_DIR
from ksxt.config import VALID_METHODS
import ksxt.models


class AsyncExchange(RestExchange):
    synchronous = False

    def __init__(self, config: Dict = None, filename: str = None):
        super().__init__(config, filename)

        self.asyncio_loop = None
        self.session: aiohttp.ClientSession = None

    async def initialize(self):
        if self.asyncio_loop is None:
            self.asyncio_loop = asyncio.get_event_loop()

        if self.session is None or (
            self.session_last_used and (time.time() - self.session_last_used > self.session_lifetime)
        ):
            if self.session:
                await self.session.close()
            self.session = aiohttp.ClientSession()
            self.session_last_used = time.time()

    async def close(self):
        if self.session:
            await self.session.close()
            self.session = None
            self.session_last_used = None

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, *args):
        await self.close()

    def check_token(func):
        async def wrapper(self, *args, **kwargs):
            if not await self.is_valid_token():
                await self.create_token()

            return await func(self, *args, **kwargs)

        return wrapper

    async def is_valid_token(self) -> bool:
        await self.load_token()
        if self.token_expired is None:
            return False

        return datetime.now(self.timezone) <= self.timezone.localize(self.token_expired)

    async def read_token(self):
        try:
            token_path = os.path.join(CONFIG_DIR, "token.toml")
            async with aiofiles.open(token_path, mode="r") as f:
                c = toml.loads(await f.read())
            return c
        except Exception as e:
            return {}

    async def load_token(self):
        try:
            data = await self.read_token()

            if self.open_key in data.keys():
                self.token = data[self.open_key]["token"]
                self.token_expired = data[self.open_key]["expired"]
        except Exception as e:
            pass

    async def save_token(self, open_key, token, expired):
        try:
            logging.info("save token")
            logging.info(open_key)
            logging.info(token)
            logging.info(expired)

            data = await self.read_token()
            if open_key not in data:
                data[open_key] = {}
            data[open_key]["token"] = token
            data[open_key]["expired"] = expired

            token_path = os.path.join(CONFIG_DIR, "token.toml")
            async with aiofiles.open(token_path, "w") as file:
                await file.write(toml.dumps(data))

            await self.load_token()
        except Exception as e:
            pass

    async def create_token(self):
        pass

    async def fetch(self, url, method="GET", headers=None, body=None, params=None):
        # Ensure that resources are initialized before the request
        await self.initialize()

        method_lower = method.lower()
        if method_lower not in VALID_METHODS:
            raise ValueError(f"Invalid HTTP method: {method}")

        session_method = getattr(self.session, method.lower())

        # TODO : Set rate limiters value when config load
        api_name = ""

        if api_name and api_name in self.rate_limiters:
            await self.rate_limiters[api_name].async_acquire()

        try:
            async with session_method(
                url,
                headers=headers,
                data=str(body).encode() if body else None,
                params=params,
                timeout=aiohttp.ClientTimeout(total=int(self.timeout / 1000)),
            ) as response:
                http_response = await response.text(errors="replace")
                json_response = self.parse_json(http_response)
                return json_response
        except (asyncio.TimeoutError, aiohttp.ClientError) as e:
            details = f"{self.id} {method} {url}"
            raise TimeoutError(details) from e
        finally:
            if (
                api_name
                and api_name in self.rate_limiters
                and isinstance(self.rate_limiters[api_name], RateLimiterContext)
            ):
                self.rate_limiters[api_name].release()

    async def fetch2(
        self, path, security_type, params={}, headers: Any | None = None, body: Any | None = None, config={}
    ):
        is_activate = self.apis[self.type][security_type][path]["activate"]
        if not is_activate:
            return {
                "response": {
                    # 성공 실패 여부
                    "success": "-1",
                    # 응답코드
                    "code": "fail",
                    # 응답메세지
                    "message": f"지원하지 않는 함수({path}) 입니다.",
                }
            }

        # if self.enableRateLimit:
        #     cost = self.calculate_rate_limiter_cost(api, method, path, params, config)
        #     self.throttle(cost)

        # self.lastRestRequestTimestamp = self.milliseconds()

        method_type = self.apis[self.type][security_type][path]["method"]
        api_type = self.apis[self.type][security_type][path]["api"]
        request = self.sign(path, security_type, method_type, api_type, headers, body, params, config)
        return await self.fetch(
            request["url"], request["method"], request["headers"], request["body"], request["params"]
        )

    # region base method
    async def fetch_markets(self, market_name: str) -> ksxt.models.KsxtMarketResponse:
        raise NotSupportedError(f"{self.id} {self.fetch_markets.__qualname__}() is not supported yet.")

    async def fetch_security(self, symbol: str, base_market: str = "KRW") -> ksxt.models.KsxtSecurityResponse:
        raise NotSupportedError(f"{self.id} {self.fetch_security.__qualname__}() is not supported yet.")

    async def fetch_ticker(self, symbol: str, base_market: str = "KRW") -> ksxt.models.KsxtTickerResponse:
        raise NotSupportedError(f"{self.id} {self.fetch_ticker.__qualname__}() is not supported yet.")

    async def fetch_orderbook(self, symbol: str, base_market: str = "KRW") -> ksxt.models.KsxtSingleOrderBookResponse:
        raise NotSupportedError(f"{self.id} {self.fetch_orderbook.__qualname__}() is not supported yet.")

    async def fetch_historical_data(
        self,
        symbol: str,
        time_frame: str,
        start: datetime | None = None,
        end: datetime | None = None,
        base_market: str = "KRW",
    ) -> ksxt.models.KsxtHistoricalDataResponse:
        raise NotSupportedError(f"{self.id} {self.fetch_historical_data.__qualname__}() is not supported yet.")

    async def fetch_is_holiday(self, dt: datetime, base_market: str = "KRW"):
        raise NotSupportedError(f"{self.id} {self.fetch_is_holiday.__qualname__}() is not supported yet.")

    async def fetch_user_info(self, base_market: str = "KRW"):
        raise NotSupportedError(f"{self.id} {self.fetch_user_info.__qualname__}() is not supported yet.")

    async def fetch_balance(
        self,
        acc_num: str,
        base_market: str = "KRW",
        excluded_symbols: list[str] | None = None,
        included_symbols: list[str] | None = None,
        filter_delisted: bool = True,
        min_amount: float = 0,
    ) -> ksxt.models.KsxtBalanceResponse:
        raise NotSupportedError(f"{self.id} {self.fetch_balance.__qualname__}() is not supported yet.")

    async def fetch_cash(self, acc_num: str, base_market: str = "KRW") -> ksxt.models.KsxtCashResponse:
        raise NotSupportedError(f"{self.id} {self.fetch_cash.__qualname__}() is not supported yet.")

    async def fetch_screener_list(self, base_market: str = "KRW"):
        raise NotSupportedError(f"{self.id} {self.fetch_screener_list.__qualname__}() is not supported yet.")

    async def fetch_screener(self, screen_id: str, base_market: str = "KRW"):
        raise NotSupportedError(f"{self.id} {self.fetch_screener.__qualname__}() is not supported yet.")

    async def fetch_deposit_history(
        self, acc_num: str, start: datetime | None = None, end: datetime | None = None, base_market: str = "KRW"
    ) -> ksxt.models.KsxtDepositHistoryResponse:
        raise NotSupportedError(f"{self.id} {self.fetch_deposit_history.__qualname__}() is not supported yet.")

    async def fetch_withdrawal_history(
        self, acc_num: str, start: datetime | None = None, end: datetime | None = None, base_market: str = "KRW"
    ) -> ksxt.models.KsxtWithdrawalHistoryResponse:
        raise NotSupportedError(f"{self.id} {self.fetch_withdrawal_history.__qualname__}() is not supported yet.")

    async def create_order(
        self,
        acc_num: str,
        symbol: str,
        ticket_type: Literal["EntryLong", "EntryShort", "ExitLong", "ExitShort"],
        otype: Literal["limit", "market"],
        price: float | None = 0,
        qty: float | None = 0,
        amount: float | None = 0,
        base_market: str = "KRW",
    ) -> ksxt.models.KsxtCreateOrderResponse:
        raise NotSupportedError(f"{self.id} {self.create_order.__qualname__}() is not supported yet.")

    async def cancel_order(
        self, acc_num: str, order_id: str, symbol: str | None = "", qty: float = 0, *args, base_market: str = "KRW"
    ) -> ksxt.models.KsxtCancelOrderResponse:
        raise NotSupportedError(f"{self.id} {self.cancel_order.__qualname__}() is not supported yet.")

    async def modify_order(
        self,
        acc_num: str,
        order_id: str,
        price: float,
        qty: float,
        *args,
        symbol: str | None = "",
        base_market: str = "KRW",
    ):
        raise NotSupportedError(f"{self.id} {self.modify_order.__qualname__}() is not supported yet.")

    async def fetch_open_order(
        self,
        acc_num: str,
        symbol: str | None = "",
        start: datetime | None = None,
        end: datetime | None = None,
        base_market: str = "KRW",
    ) -> ksxt.models.KsxtOpenOrderResponse:
        raise NotSupportedError(f"{self.id} {self.fetch_open_order.__qualname__}() is not supported yet.")

    async def fetch_closed_order(
        self,
        acc_num: str,
        symbol: str | None = "",
        start: datetime | None = None,
        end: datetime | None = None,
        base_market: str = "KRW",
    ) -> ksxt.models.KsxtClosedOrderResponse:
        raise NotSupportedError(f"{self.id} {self.fetch_closed_order.__qualname__}() is not supported yet.")

    async def reserve_order(
        self, acc_num: str, symbol: str, price: float, qty: float, target_date: str, base_market: str = "KRW"
    ):
        raise NotSupportedError(f"{self.id} {self.reserve_order.__qualname__}() is not supported yet.")

    # endregion base method

    async def sleep(self, milliseconds):
        return await asyncio.sleep(milliseconds / 1000)
