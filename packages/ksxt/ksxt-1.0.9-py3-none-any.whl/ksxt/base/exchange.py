import collections
import json
from datetime import datetime
import time
import pytz
from typing import Dict
import ast

from requests import Session
import urllib.parse as _urlencode

from ksxt.base.types import IndexType
from ksxt.models.common import CommonResponse, CommonResponseHeader


class Exchange:
    id = None
    name = None
    version = None
    is_dev = False

    session = None
    # 세션 유효 시간 (초)
    session_lifetime = 10
    # 세션의 마지막 사용 시간
    session_last_used: time = None

    timeout = 10000  # milliseconds = seconds * 1000
    synchronous = True

    required_credentials = {
        "open_key": False,
        "secret_key": False,
        "uid": False,
        "login": False,
        "password": False,
        "token": False,
    }

    def __init__(self):
        if not self.session and self.synchronous:
            self.session = Session()

    def __del__(self):
        if self.session:
            try:
                self.session.close()
            except Exception as e:
                pass

    def __str__(self):
        return self.name

    # region public feeder
    def fetch_markets(self, market_name: str):
        """
        Market 정보 조회

        Args:
            market_name (str, optional): Market 구분 코드.
        """
        pass

    def fetch_security(self, symbol: str, base_market: str = "KRW"):
        """
        종목 정보 조회

        Args:
            symbol (str): 종목코드
            base_market (str, optional): Market 구분 코드. Defaults to 'KRW'.
        """
        pass

    def fetch_ticker(self, symbol: str, base_market: str = "KRW"):
        """
        시세 정보 조회

        Args:
            symbol (str): 종목코드
            base_market (str, optional): Market 구분 코드. Defaults to 'KRW'.
        """
        pass

    def fetch_historical_data(
        self,
        symbol: str,
        time_frame: str,
        start: datetime | None = None,
        end: datetime | None = None,
        base_market: str = "KRW",
    ):
        """
        과거 봉 정보 조회

        Args:
            symbol (str): 종목코드
            time_frame (str): 봉조회기준
            start (datetime | None, optional): 조회 시작일. Defaults to None.
            end (datetime | None, optional): 조회 종료일. Defaults to None.
            base_market (str, optional): Market 구분 코드. Defaults to 'KRW'.
        """
        pass

    def resample(self, df, timeframe: str, offset):
        ohlcv = {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}

        result = df.resample(timeframe.upper(), offset=offset).apply(ohlcv)
        return result

    def fetch_is_holiday(self, dt: datetime, base_market: str = "KRW"):
        """
        휴장일 조회

        Args:
            dt (datetime): 조회 날짜 (YYYYMMDD)
            base_market (str, optional): Market 구분 코드. Defaults to 'KRW'.
        """
        pass

    # endregion public feeder

    # region private feeder
    def fetch_user_info(self, base_market: str = "KRW"):
        """
        회원 정보 조회

        Args:
            base_market (str, optional): Market 구분 코드. Defaults to 'KRW'.
        """
        pass

    def fetch_trade_fee(self, symbol: str, base_market: str = "KRW"):
        """
        종목의 거래 수수료 정보 조회

        Args:
            symbol (str): 종목코드
            base_market (str, optional): Market 구분 코드. Defaults to 'KRW'.
        """
        pass

    def fetch_balance(
        self,
        acc_num: str,
        base_market: str = "KRW",
        excluded_symbols: list[str] | None = None,
        included_symbols: list[str] | None = None,
        filter_delisted: bool = True,
        min_amount: float = 0,
    ):
        """
        보유 자산 조회

        Args:
            acc_num (str): 계좌 번호
            base_market (str, optional): Market 구분 코드. Defaults to 'KRW'.
            excluded_symbols (list[str] | None, optional): 제외할 종목 리스트. Defaults to None.
            included_symbols (list[str] | None, optional): 포함할 종목 리스트. Defaults to None.
            filter_delisted (bool, optional): 거래 지원 종료되거나 상장 폐지된 종목 필터링 여부. Defaults to True.
            min_amount (float, optional): 최소 자산 금액 필터링. Defaults to 0.
        """
        pass

    def fetch_cash(self, acc_num: str, base_market: str = "KRW"):
        """
        예수금 조회

        Args:
            acc_num (str): 계좌 번호
            base_market (str, optional): Market 구분 코드. Defaults to 'KRW'.
        """
        pass

    def fetch_screener_list(self, base_market: str = "KRW"):
        """
        조건식 리스트 조회

        Returns:
            _type_: 조건식 리스트
        """
        pass

    def fetch_screener(self, screen_id: str, base_market: str = "KRW"):
        """
        조건식 조회 결과

        Args:
            screen_id (str): Screener 조회 값 (조건식 조회 결과)
            base_market (str, optional): Market 구분 코드. Defaults to 'KRW'.
        """
        pass

    def fetch_deposit_history(
        self, acc_num: str, start: datetime | None = None, end: datetime | None = None, base_market: str = "KRW"
    ):
        """
        입금 내역 조회

        Args:
            acc_num (str): 계좌 번호
            start (datetime | None, optional): 조회 시작일. Defaults to None.
            end (datetime | None, optional): 조회 종료일. Defaults to None.
            base_market (str, optional): Market 구분 코드. Defaults to 'KRW'.
        """
        pass

    def fetch_withdrawal_history(
        self, acc_num: str, start: datetime | None = None, end: datetime | None = None, base_market: str = "KRW"
    ):
        """
        출금 내역 조회

        Args:
            acc_num (str): 계좌 번호
            start (datetime | None, optional): 조회 시작일. Defaults to None.
            end (datetime | None, optional): 조회 종료일. Defaults to None.
            base_market (str, optional): Market 구분 코드. Defaults to 'KRW'.
        """
        pass

    # endregion private feeder

    # region broker
    def create_order(
        self,
        acc_num: str,
        symbol: str,
        ticket_type: str,
        price: float,
        qty: float,
        amount: float,
        otype: str,
        base_market: str = "KRW",
    ):
        """
        주문 발행

        Args:
            acc_num (str): 계좌정보(계좌번호, 지갑정보)
            symbol (str): 종목정보(종목코드)
            ticket_type (str): EntryLong, EntryShort, ExitLong, ExitShort, ...
            price (float): 가격 (지정가 시 필수)
            qty (float): 수량 (매도 시 필수.)
            amount (float): 총금액 (시장가 매수 시 필수)
            otype (str): market(시장가), limit(지정가), ...
            base_market (str, optional): Market 구분 코드. Defaults to 'KRW'.
        """
        pass

    def cancel_order(
        self, acc_num: str, order_id: str, symbol: str | None = "", qty: float = 0, *args, base_market: str = "KRW"
    ):
        """
        미체결 주문 취소

        Args:
            acc_num (str): 계좌정보(계좌번호, 지갑정보)
            order_id (str): 주문 정보(주문 id)
            symbol (str | None, optional): 종목정보(종목코드). Defaults to ''.
            qty (float, optional): 수량. Defaults to 0..
            base_market (str, optional): Market 구분 코드. Defaults to 'KRW'.
        """
        pass

    def fetch_open_order(
        self,
        acc_num: str,
        symbol: str | None = "",
        start: datetime | None = None,
        end: datetime | None = None,
        base_market: str = "KRW",
    ):
        """
        미체결 주문 내역 조회

        Args:
            acc_num (str): 계좌정보(계좌번호, 지갑정보)
            symbol (str | None, optional): 종목정보(종목코드) Defaults to ''.
            start (datetime | None, optional): 조회 시작일자. Defaults to None.
            end (datetime | None, optional): 조회 종료일자. Defaults to None.
            base_market (str, optional): Market 구분 코드. Defaults to 'KRW'.
        """
        pass

    def fetch_closed_order(
        self,
        acc_num: str,
        symbol: str | None = "",
        start: datetime | None = None,
        end: datetime | None = None,
        base_market: str = "KRW",
    ):
        """
        체결 주문 내역 조회

        Args:
            acc_num (str): 계좌정보(계좌번호, 지갑정보)
            symbol (str | None, optional): 종목정보(종목코드) Defaults to ''.
            start (datetime | None, optional): 조회 시작일자. Defaults to None.
            end (datetime | None, optional): 조회 종료일자. Defaults to None.
            base_market (str, optional): Market 구분 코드. Defaults to 'KRW'.
        """
        pass

    def reserve_order(
        self, acc_num: str, symbol: str, price: float, qty: float, target_date: str, base_market: str = "KRW"
    ):
        """
        예약 주문 발행

        Args:
            acc_num (str): 계좌정보(계좌번호, 지갑정보)
            symbol (str): 종목정보(종목코드)
            price (float): 가격
            qty (float): 수량
            target_date (str): 예약일자
            base_market (str, optional): Market 구분 코드. Defaults to 'KRW'.
        """
        pass

    # endregion broker

    def create_common_response(self, success: str, msg_code: str, msg: str, info: dict) -> CommonResponse:
        return CommonResponse(success=success, msg_code=msg_code, msg=msg, info=info)

    def create_common_header(self, request_params: dict) -> CommonResponseHeader:
        return CommonResponseHeader(request_params=request_params)

    # region utils
    @staticmethod
    def now(base_market: str = "KRW"):
        if base_market == "KRW":
            return datetime.now(tz=pytz.timezone("Asia/Seoul"))
        elif base_market == "USD":
            return datetime.now(tz=pytz.timezone("US/Eastern"))
        else:
            return datetime.now(tz=pytz.utc)

    @staticmethod
    def seconds():
        return int(time.time())

    @staticmethod
    def milliseconds():
        return int(time.time() * 1_000)

    @staticmethod
    def set_attr(self, attrs):
        for key in attrs:
            if hasattr(self, key) and isinstance(getattr(self, key), dict):
                setattr(self, key, Exchange.deep_extend(getattr(self, key), attrs[key]))
            else:
                setattr(self, key, attrs[key])

    @staticmethod
    def extend(*args):
        if args is not None:
            result = None
            if type(args[0]) is collections.OrderedDict:
                result = collections.OrderedDict()
            else:
                result = {}

            for arg in args:
                result.update(arg)

            return result

        return {}

    @staticmethod
    def deep_extend(*args):
        result = None
        for arg in args:
            if isinstance(arg, dict):
                if not isinstance(result, dict):
                    result = {}
                for key in arg:
                    result[key] = Exchange.deep_extend(result[key] if key in result else None, arg[key])
            else:
                result = arg

        return result

    @staticmethod
    def omit(d, *args):
        if isinstance(d, dict):
            result = d.copy()
            for arg in args:
                if type(arg) is list:
                    for key in arg:
                        if key in result:
                            del result[key]
                else:
                    if arg in result:
                        del result[arg]
            return result
        return d

    @staticmethod
    def implode_params(string, params):
        if isinstance(params, dict):
            for key in params:
                if not isinstance(params[key], list):
                    string = string.replace("{" + key + "}", str(params[key]))
        return string

    @staticmethod
    def urlencode(params={}, doseq=False):
        new_params = params.copy()
        for key, value in params.items():
            if isinstance(value, bool):
                new_params[key] = "true" if value else "false"
        return _urlencode.urlencode(new_params, doseq, quote_via=_urlencode.quote)

    def calculate_rate_limiter_cost(self, api, method, path, params, config={}):
        return self.safe_value(config, "cost", 1)

    def parse_json(self, http_response):
        return json.loads(http_response, parse_float=str, parse_int=str)

    # region safe method
    @staticmethod
    def key_exists(dictionary, key):
        if hasattr(dictionary, "__getitem__") and not isinstance(dictionary, str):
            if isinstance(dictionary, list) and type(key) is not int:
                return False
            try:
                value = dictionary[key]
                return value is not None and value != ""
            except LookupError:
                return False
        return False

    @staticmethod
    def safe_value(dictionary, key, default_value=None):
        return dictionary[key] if Exchange.key_exists(dictionary, key) else default_value

    @staticmethod
    def safe_string(dictionary, key, default_value=""):
        return str(dictionary[key]) if Exchange.key_exists(dictionary, key) else default_value

    @staticmethod
    def safe_number(dictionary, key, default_value=0):
        value = Exchange.safe_string(dictionary, key)
        if value == "":
            return default_value

        try:
            return float(value)
        except Exception:
            return default_value

    @staticmethod
    def safe_boolean(dictionary, key, default_value=False):
        value = Exchange.safe_string(dictionary, key)
        if value == "":
            return default_value

        try:
            return bool(ast.literal_eval(value.capitalize()))
        except (ValueError, SyntaxError):
            return default_value

    # endregion safe method

    @staticmethod
    def keysort(dictionary):
        return collections.OrderedDict(sorted(dictionary.items(), key=lambda t: t[0]))

    @staticmethod
    def sort_by(array, key, descending=False):
        return sorted(array, key=lambda k: k[key] if k[key] is not None else "", reverse=descending)

    @staticmethod
    def sort_by_2(array, key1, key2, descending=False):
        return sorted(
            array,
            key=lambda k: (k[key1] if k[key1] is not None else "", k[key2] if k[key2] is not None else ""),
            reverse=descending,
        )

    @staticmethod
    def index_by(array, key):
        result = {}
        if type(array) is dict:
            array = Exchange.keysort(array).values()
        is_int_key = isinstance(key, int)
        for element in array:
            if ((is_int_key and (key < len(element))) or (key in element)) and (element[key] is not None):
                k = element[key]
                result[k] = element
        return result

    @staticmethod
    def to_array(value):
        return list(value.values()) if type(value) is dict else value

    def filter_by_array(self, objects, key: IndexType, values=None, indexed=True):
        objects = self.to_array(objects)

        # return all of them if no values were passed
        if values is None or not values:
            return self.index_by(objects, key) if indexed else objects

        results = []
        for i in range(0, len(objects)):
            if self.in_array(objects[i][key], values):
                results.append(objects[i])

        return self.index_by(results, key) if indexed else results

    # endregion
