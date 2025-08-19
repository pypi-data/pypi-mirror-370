import json
import logging
import tomllib
import toml
import os
from pathlib import Path

from typing import Any, Dict, List, Literal

from datetime import datetime, UTC
import pytz
import time

from ksxt.base.rate_limiter import (
    RateLimiterContext,
    RequestRateLimiter,
    TimeBasedRateLimiter,
)
from ksxt.base.errors import NotSupportedError
from ksxt.base.exchange import Exchange
from ksxt.config import CONFIG_DIR
import ksxt.models


class RestExchange(Exchange):
    required_credentials = {
        "open_key": True,
        "secret_key": True,
        "uid": False,
        "login": False,
        "password": False,
        "token": False,
    }

    headers = None
    token = None
    token_expired = None
    type = "rest"

    rate_limit = 2000  # milliseconds = seconds * 1000
    lastRestRequestTimestamp = 0
    timezone = pytz.timezone("UTC")

    def __init__(self, config: Dict = None, filename: str = None) -> None:
        super().__init__()

        self.rate_limiters: Dict[str, RateLimiterContext] = {}

        self.headers = dict() if self.headers is None else self.headers

        if config is None:
            config = {}

        # settings = self.deep_extend(self.describe(), config)
        # Exchange.set_attr(self, settings)

        settings = self.deep_extend(config)
        Exchange.set_attr(self, settings)

        apis = self._get_api_from_file(filename)
        Exchange.set_attr(self, apis)

    def _get_api_from_file(self, filename: str) -> Dict[str, Any]:
        if filename is None:
            raise ValueError("Configuration filename cannot be None.")

        config_path = os.path.join(CONFIG_DIR, filename)

        if Path(filename).suffix != ".toml":
            raise ValueError(f"Unsupported file format: {Path(filename).suffix}")

        with open(config_path, mode="rb") as f:
            config = tomllib.load(f)

        self._setup_rate_limiters(config)
        return config

    def _setup_rate_limiters(self, config: Dict[str, Any]):
        """RateLimiter 설정을 구성하는 메서드"""
        default_rate_limit = config.get("rate_limit", 1000)  # 최상위 rate_limit 값 가져오기

        apis = config.get("apis", {}).get("rest", {})

        def traverse_apis(api_section, section_name="", self=self):
            for key, value in api_section.items():
                if not isinstance(value, dict):
                    continue

                if "url" in value:  # "url"이 있는 경우, API 엔드포인트로 간주
                    rate_limit = value.get("rate_limit", default_rate_limit)
                    rate_limit_period = value.get("rate_limit_period", 1.0)

                    # 전략 패턴을 이용한 RateLimiter 생성
                    if rate_limit_period > 1.0:
                        strategy = TimeBasedRateLimiter(period=rate_limit_period)
                    else:
                        strategy = RequestRateLimiter(max_requests=rate_limit, period=1.0)

                    # API 이름을 구성
                    api_name = f"{section_name}.{key}" if section_name else key
                    self.rate_limiters[api_name] = RateLimiterContext(strategy)
                else:
                    # value가 딕셔너리지만 "url"이 없는 경우, 하위 섹션으로 간주하고 재귀 호출
                    traverse_apis(value, f"{section_name}.{key}" if section_name else key)

        traverse_apis(apis)

    def check_token(func):
        def wrapper(self, *args, **kwargs):
            if not self.is_valid_token():
                self.create_token()

            return func(self, *args, **kwargs)

        return wrapper

    def is_valid_token(self) -> bool:
        self.load_token()
        if self.token_expired is None:
            return False

        return datetime.now(self.timezone) <= self.timezone.localize(self.token_expired)

    def read_token(self):
        try:
            token_path = os.path.join(CONFIG_DIR, "token.toml")
            with open(token_path, mode="r") as f:
                c = toml.load(f)
            return c
        except Exception as e:
            return {}

    def load_token(self):
        try:
            data = self.read_token()

            if self.open_key in data.keys():
                self.token = data[self.open_key]["token"]
                self.token_expired = data[self.open_key]["expired"]
        except Exception as e:
            pass

    def save_token(self, open_key, token, expired):
        try:
            logging.info("save token")
            logging.info(open_key)
            logging.info(token)
            logging.info(expired)

            data = self.read_token()
            if open_key not in data:
                data[open_key] = {}
            data[open_key]["token"] = token
            data[open_key]["expired"] = expired

            token_path = os.path.join(CONFIG_DIR, "token.toml")
            with open(token_path, "w") as file:
                toml.dump(data, file)

            self.load_token()
        except Exception as e:
            pass

    def create_token(self):
        pass

    def prepare_request_headers(self, headers=None):
        headers = headers or {}

        if self.session:
            headers.update(self.session.headers)

        self.headers.update(headers)

        headers.update({"content-type": "application/json"})
        # headers.update({'appKey':self.open_key})
        # headers.update({'appsecret':self.secret_key})

        return headers

    def throttle(self, cost=None):
        now = float(self.milliseconds())
        elapsed = now - self.lastRestRequestTimestamp
        cost = 1 if cost is None else cost
        sleep_time = self.rate_limit * cost
        if elapsed < sleep_time:
            delay = sleep_time - elapsed
            time.sleep(delay / 1000.0)

    def fetch(self, url, method="GET", headers=None, body=None, params=None):
        request_headers = headers
        request_body = body
        request_params = params

        self.session.cookies.clear()

        http_response = None
        http_status_code = None
        http_status_text = None
        json_response = None

        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=request_headers,
                data=request_body,
                params=request_params,
                timeout=int(self.timeout / 1000),
            )

            response.encoding = "utf-8"

            headers = response.headers
            http_status_code = response.status_code
            http_status_text = response.reason
            http_response = response.text.strip()
            json_response = self.parse_json(http_response)

        except TimeoutError as e:
            details = " ".join([self.id, method, url])
            raise TimeoutError(details) from e

        return json_response

    def is_activate(self, path, security_type) -> bool:
        return self.apis[self.type][security_type][path]["activate"]

    def sign(
        self,
        path,
        security_type,
        method_type,
        api_type: Any = "public",
        headers: Any | None = None,
        body: Any | None = None,
        params: Any | None = None,
        config={},
    ):
        pass

    def fetch2(self, path, security_type, params={}, headers: Any | None = None, body: Any | None = None, config={}):
        is_activate = self.is_activate(path=path, security_type=security_type)
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
        return self.fetch(request["url"], request["method"], request["headers"], request["body"], request["params"])

    def request(self, path, security_type, params={}, headers: Any | None = None, body: Any | None = None, config={}):
        return self.fetch2(path, security_type, params, headers, body, config)

    # region base method
    def create_token(self) -> ksxt.models.KsxtTokenResponse:
        raise NotSupportedError(f"{self.id} {self.create_token.__qualname__}() is not supported yet.")

    @check_token
    def fetch_markets(self, market_name: str) -> ksxt.models.KsxtMarketResponse:
        raise NotSupportedError(f"{self.id} {self.fetch_markets.__qualname__}() is not supported yet.")

    @check_token
    def fetch_security(self, symbol: str, base_market: str = "KRW") -> ksxt.models.KsxtSecurityResponse:
        raise NotSupportedError(f"{self.id} {self.fetch_security.__qualname__}() is not supported yet.")

    @check_token
    def fetch_ticker(self, symbol: str, base_market: str = "KRW") -> ksxt.models.KsxtTickerResponse:
        raise NotSupportedError(f"{self.id} {self.fetch_ticker.__qualname__}() is not supported yet.")

    @check_token
    def fetch_orderbook(self, symbol: str, base_market: str = "KRW") -> ksxt.models.KsxtSingleOrderBookResponse:
        raise NotSupportedError(f"{self.id} {self.fetch_orderbook.__qualname__}() is not supported yet.")

    @check_token
    def fetch_historical_data_index(
        self,
        symbol: str,
        time_frame: str,
        start: datetime | None = None,
        end: datetime | None = None,
        base_market: str = "KRW",
    ) -> ksxt.models.KsxtHistoricalDataResponse:
        raise NotSupportedError(f"{self.id} {self.fetch_historical_data_index.__qualname__}() is not supported yet.")

    @check_token
    def fetch_historical_data(
        self,
        symbol: str,
        time_frame: str,
        start: datetime | None = None,
        end: datetime | None = None,
        base_market: str = "KRW",
    ) -> ksxt.models.KsxtHistoricalDataResponse:
        raise NotSupportedError(f"{self.id} {self.fetch_historical_data.__qualname__}() is not supported yet.")

    @check_token
    def fetch_is_holiday(self, dt: datetime, base_market: str = "KRW") -> ksxt.models.KsxtHolidayResponse:
        raise NotSupportedError(f"{self.id} {self.fetch_is_holiday.__qualname__}() is not supported yet.")

    @check_token
    def fetch_user_info(self, base_market: str = "KRW"):
        raise NotSupportedError(f"{self.id} {self.fetch_user_info.__qualname__}() is not supported yet.")

    @check_token
    def fetch_balance(
        self,
        acc_num: str,
        base_market: str = "KRW",
        excluded_symbols: list[str] | None = None,
        included_symbols: list[str] | None = None,
        filter_delisted: bool = True,
        min_amount: float = 0,
    ) -> ksxt.models.KsxtBalanceResponse:
        raise NotSupportedError(f"{self.id} {self.fetch_balance.__qualname__}() is not supported yet.")

    @check_token
    def fetch_cash(self, acc_num: str, base_market: str = "KRW") -> ksxt.models.KsxtCashResponse:
        raise NotSupportedError(f"{self.id} {self.fetch_cash.__qualname__}() is not supported yet.")

    @check_token
    def fetch_trade_fee(self, symbol: str, base_market: str = "KRW") -> ksxt.models.KsxtTradeFeeResponse:
        raise NotSupportedError(f"{self.id} {self.fetch_trade_fee.__qualname__}() is not supported yet.")

    @check_token
    def fetch_screener_list(self, base_market: str = "KRW"):
        raise NotSupportedError(f"{self.id} {self.fetch_screener_list.__qualname__}() is not supported yet.")

    @check_token
    def fetch_screener(self, screen_id: str, base_market: str = "KRW"):
        raise NotSupportedError(f"{self.id} {self.fetch_screener.__qualname__}() is not supported yet.")

    @check_token
    def fetch_deposit_history(
        self, acc_num: str, start: datetime | None = None, end: datetime | None = None, base_market: str = "KRW"
    ) -> ksxt.models.KsxtDepositHistoryResponse:
        raise NotSupportedError(f"{self.id} {self.fetch_deposit_history.__qualname__}() is not supported yet.")

    @check_token
    def fetch_withdrawal_history(
        self, acc_num: str, start: datetime | None = None, end: datetime | None = None, base_market: str = "KRW"
    ) -> ksxt.models.KsxtWithdrawalHistoryResponse:
        raise NotSupportedError(f"{self.id} {self.fetch_withdrawal_history.__qualname__}() is not supported yet.")

    @check_token
    def create_order(
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

    @check_token
    def cancel_order(
        self, acc_num: str, order_id: str, symbol: str | None = "", qty: float = 0, *args, base_market: str = "KRW"
    ) -> ksxt.models.KsxtCancelOrderResponse:
        raise NotSupportedError(f"{self.id} {self.cancel_order.__qualname__}() is not supported yet.")

    @check_token
    def modify_order(
        self,
        acc_num: str,
        order_id: str,
        price: float,
        qty: float,
        *args,
        symbol: str | None = "",
        base_market: str = "KRW",
    ) -> ksxt.models.KsxtModifyOrderResponse:
        raise NotSupportedError(f"{self.id} {self.modify_order.__qualname__}() is not supported yet.")

    @check_token
    def fetch_open_order(
        self,
        acc_num: str,
        symbol: str | None = "",
        start: datetime | None = None,
        end: datetime | None = None,
        base_market: str = "KRW",
    ) -> ksxt.models.KsxtOpenOrderResponse:
        raise NotSupportedError(f"{self.id} {self.fetch_open_order.__qualname__}() is not supported yet.")

    @check_token
    def fetch_closed_order(
        self,
        acc_num: str,
        symbol: str | None = "",
        start: datetime | None = None,
        end: datetime | None = None,
        base_market: str = "KRW",
    ) -> ksxt.models.KsxtClosedOrderResponse:
        raise NotSupportedError(f"{self.id} {self.fetch_closed_order.__qualname__}() is not supported yet.")

    @check_token
    def fetch_open_order_detail(
        self, acc_num: str, order_ids: List[str], base_market: str = "KRW"
    ) -> ksxt.models.KsxtOpenOrderResponse:
        raise NotSupportedError(f"{self.id} {self.fetch_open_order_detail.__qualname__}() is not supported yet.")

    @check_token
    def fetch_closed_order_detail(
        self, acc_num: str, order_ids: List[str], base_market: str = "KRW"
    ) -> ksxt.models.KsxtOpenOrderResponse:
        raise NotSupportedError(f"{self.id} {self.fetch_closed_order_detail.__qualname__}() is not supported yet.")

    @check_token
    def reserve_order(
        self, acc_num: str, symbol: str, price: float, qty: float, target_date: str, base_market: str = "KRW"
    ):
        raise NotSupportedError(f"{self.id} {self.reserve_order.__qualname__}() is not supported yet.")

    # endregion base method
