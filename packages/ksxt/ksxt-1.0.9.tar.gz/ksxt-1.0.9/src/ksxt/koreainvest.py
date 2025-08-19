import json
import os
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Literal, Optional

import pytz

from ksxt.api.koreainvest import ImplicitAPI
from ksxt.base.rest_exchange import RestExchange
from ksxt.market.manager import MarketManager
from ksxt.parser.koreainvest import KoreaInvestParser

import ksxt.models


class KoreaInvest(RestExchange, ImplicitAPI):
    def __init__(self, config: Dict = None) -> None:
        super().__init__(config, "koreainvest.toml")
        self.parser = KoreaInvestParser()
        self.timezone = pytz.timezone("Asia/Seoul")

    def is_activate(self, path, security_type) -> bool:
        mode = "dev" if self.is_dev == True else "app"

        tr_id = self.apis[self.type][security_type][path][mode]["tr_id"]

        if security_type != "token" and not bool(tr_id):
            return False

        return super().is_activate(path=path, security_type=security_type)

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
        mode = "dev" if self.is_dev == True else "app"

        host_url = self.apis[self.type][mode]["hostname"]
        destination = self.apis[self.type][security_type][path]["url"]
        version = self.apis[self.type]["version"]
        params["version"] = version
        destination = self.implode_params(destination, params)

        url = f"{host_url}/{destination}"

        tr_id = self.apis[self.type][security_type][path][mode]["tr_id"]
        authorization_token = f"Bearer {self.token}"

        if api_type == "private":
            if headers is None:
                headers = {}
                headers.update(
                    {
                        "content-type": "application/json; charset=utf-8",
                        "authorization": authorization_token,
                        "appkey": self.open_key,
                        "appsecret": self.secret_key,
                        "tr_id": tr_id,
                        "custtype": "P",
                    }
                )

        if method_type.upper() == "POST":
            body = json.dumps(params)
            params = {}

        return {"url": url, "method": method_type, "headers": headers, "body": body, "params": params}

    def create_token(self) -> ksxt.models.KsxtTokenResponse:
        params = {"grant_type": "client_credentials", "appkey": self.open_key, "appsecret": self.secret_key}

        common_header = self.create_common_header(request_params=params)

        response = self.public_post_generate_token(self.extend(params))

        common_response = self.get_common_response(response=response)
        if common_response.success != "0":
            return ksxt.models.KsxtTokenResponse(header=common_header, response=common_response, info=None)

        parsed_info = self.parser.parse_token(response=response)

        self.save_token(self.open_key, parsed_info.access_token, expired=parsed_info.expired_datetime)

        return ksxt.models.KsxtTokenResponse(header=common_header, response=common_response, info=parsed_info)

    def get_common_response(self, response):
        if "error_code" in response:
            return self.create_common_response(
                success="1",
                msg_code=self.safe_string(response, "error_code"),
                msg=self.safe_string(response, "error_description"),
                info=response,
            )

        if "rt_cd" in response and response["rt_cd"] != "0":
            return self.create_common_response(
                success="1",
                msg_code=self.safe_string(response, "msg_cd"),
                msg=self.safe_string(response, "msg1"),
                info=response,
            )

        if "response" in response and response["response"]["success"] != "0":
            return self.create_common_response(
                success="1",
                msg_code=self.safe_string(response["response"], "code"),
                msg=self.safe_string(response["response"], "message"),
                info=response,
            )

        return self.create_common_response(
            success="0",
            msg_code=self.safe_string(response, "msg_cd"),
            msg=self.safe_string(response, "msg1"),
            info=response,
        )

    @RestExchange.check_token
    def fetch_balance(
        self,
        acc_num: str,
        base_market: str = "KRW",
        excluded_symbols: list[str] | None = None,
        included_symbols: list[str] | None = None,
        filter_delisted: bool = True,
        min_amount: float = 0,
    ) -> ksxt.models.KsxtBalanceResponse:
        if base_market == "KRW":
            params = {
                "CANO": acc_num[:8],
                "ACNT_PRDT_CD": acc_num[-2:],
                "AFHR_FLPR_YN": "N",
                "OFL_YN": "",
                "INQR_DVSN": "01",
                "UNPR_DVSN": "01",
                "FUND_STTL_ICLD_YN": "N",
                "FNCG_AMT_AUTO_RDPT_YN": "N",
                "PRCS_DVSN": "01",
                "CTX_AREA_FK100": "",
                "CTX_AREA_NK100": "",
            }
        else:
            assert ValueError(f"{base_market} is not valid value")

        common_header = self.create_common_header(request_params=params)

        response = self.private_get_fetch_balance(self.extend(params))

        common_response = self.get_common_response(response=response)
        if common_response.success != "0":
            return ksxt.models.KsxtBalanceResponse(header=common_header, response=common_response, info=None)

        parsed_info = self.parser.parse_balance(
            response=response,
            base_market=base_market,
            excluded_symbols=excluded_symbols,
            included_symbols=included_symbols,
            filter_delisted=filter_delisted,
            min_amount=min_amount,
        )

        return ksxt.models.KsxtBalanceResponse(header=common_header, response=common_response, info=parsed_info)

    @RestExchange.check_token
    def fetch_cash(self, acc_num: str, base_market: str = "KRW") -> ksxt.models.KsxtCashResponse:
        if base_market == "KRW":
            params = {
                "CANO": acc_num[:8],
                "ACNT_PRDT_CD": acc_num[-2:],
                "AFHR_FLPR_YN": "N",
                "OFL_YN": "",
                "INQR_DVSN": "01",
                "UNPR_DVSN": "01",
                "FUND_STTL_ICLD_YN": "N",
                "FNCG_AMT_AUTO_RDPT_YN": "N",
                "PRCS_DVSN": "01",
                "CTX_AREA_FK100": "",
                "CTX_AREA_NK100": "",
            }
        else:
            assert ValueError(f"{base_market} is not valid value")

        common_header = self.create_common_header(request_params=params)

        response = self.private_get_fetch_cash(self.extend(params))

        common_response = self.get_common_response(response=response)
        if common_response.success != "0":
            return ksxt.models.KsxtCashResponse(header=common_header, response=common_response, info=None)

        parsed_info = self.parser.parse_cash(response=response, base_market=base_market)

        return ksxt.models.KsxtCashResponse(header=common_header, response=common_response, info=parsed_info)

    @RestExchange.check_token
    def fetch_orderbook(self, symbol: str, base_market: str = "KRW") -> ksxt.models.KsxtSingleOrderBookResponse:
        if base_market == "KRW":
            params = {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": symbol}
        else:
            assert ValueError(f"{base_market} is not valid value")

        common_header = self.create_common_header(request_params=params)

        response = self.private_get_fetch_orderbook(self.extend(params))

        common_response = self.get_common_response(response=response)
        if common_response.success != "0":
            return ksxt.models.KsxtSingleOrderBookResponse(header=common_header, response=common_response, info=None)

        parsed_info = self.parser.parse_orderbook(response=response, base_market=base_market)

        return ksxt.models.KsxtSingleOrderBookResponse(header=common_header, response=common_response, info=parsed_info)

    @RestExchange.check_token
    def fetch_security(self, symbol: str, base_market: str = "KRW") -> ksxt.models.KsxtSecurityResponse:
        if base_market == "KRW":
            params = {"PRDT_TYPE_CD": "300", "PDNO": symbol}
        else:
            assert ValueError(f"{base_market} is not valid value")

        common_header = self.create_common_header(request_params=params)

        response = self.private_get_fetch_security_info(self.extend(params))

        common_response = self.get_common_response(response=response)
        if common_response.success != "0":
            return ksxt.models.KsxtSecurityResponse(header=common_header, response=common_response, info=None)

        parsed_info = self.parser.parse_security(response=response, base_market=base_market)

        return ksxt.models.KsxtSecurityResponse(header=common_header, response=common_response, info=parsed_info)

    @RestExchange.check_token
    def fetch_ticker(self, symbol: str, base_market: str = "KRW") -> ksxt.models.KsxtTickerResponse:
        if base_market == "KRW":
            params = {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": symbol}
        else:
            assert ValueError(f"{base_market} is not valid value")

        common_header = self.create_common_header(request_params=params)

        response = self.private_get_fetch_ticker_price(self.extend(params))

        common_response = self.get_common_response(response=response)
        if common_response.success != "0":
            return ksxt.models.KsxtTickerResponse(header=common_header, response=common_response, info=None)

        parsed_info = self.parser.parse_ticker(response=response, base_market=base_market)

        return ksxt.models.KsxtTickerResponse(header=common_header, response=common_response, info=parsed_info)

    @RestExchange.check_token
    def fetch_historical_data_index(
        self,
        symbol: str,
        time_frame: str,
        start: datetime | None = None,
        end: datetime | None = None,
        base_market: str = "KRW",
    ) -> ksxt.models.KsxtHistoricalDataResponse:
        if time_frame.endswith("D"):
            param_code = "D"
        elif time_frame.endswith("W") or time_frame.endswith("w"):
            param_code = "W"
        elif time_frame.endswith("M"):
            param_code = "M"
        elif time_frame.endswith("Y"):
            param_code = "Y"
        else:
            assert ValueError(f"{time_frame} is not valid value")

        if start is None:
            start = self.now(base_market) - timedelta(days=50)
        if end is None:
            end = self.now(base_market)

        if base_market == "KRW":
            params = {
                "FID_COND_MRKT_DIV_CODE": "U",
                "FID_INPUT_ISCD": symbol,
                "FID_INPUT_DATE_1": start.strftime("%Y%m%d"),
                "FID_INPUT_DATE_2": end.strftime("%Y%m%d"),
                "FID_PERIOD_DIV_CODE": param_code,
            }
        else:
            assert ValueError(f"{base_market} is not valid value")

        common_header = self.create_common_header(request_params=params)

        response = self.private_get_fetch_index_ohlcv(self.extend(params))

        common_response = self.get_common_response(response=response)
        if common_response.success != "0":
            return ksxt.models.KsxtHistoricalDataResponse(header=common_header, response=common_response, info=None)

        parsed_response = self.parser.parse_historical_index_data(
            response=response, symbol=symbol, start=start, end=end, base_market=base_market
        )

        return ksxt.models.KsxtHistoricalDataResponse(
            header=common_header, response=common_response, info=parsed_response
        )

    @RestExchange.check_token
    def fetch_historical_data(
        self,
        symbol: str,
        time_frame: str,
        start: datetime | None = None,
        end: datetime | None = None,
        base_market: str = "KRW",
    ) -> ksxt.models.KsxtHistoricalDataResponse:
        if time_frame.endswith("D"):
            param_code = "D"
        elif time_frame.endswith("W") or time_frame.endswith("w"):
            param_code = "W"
        elif time_frame.endswith("M"):
            param_code = "M"
        elif time_frame.endswith("Y"):
            param_code = "Y"
        else:
            assert ValueError(f"{time_frame} is not valid value")

        if start is None:
            start = self.now(base_market) - timedelta(days=100)
        if end is None:
            end = self.now(base_market)

        if base_market == "KRW":
            params = {
                "FID_COND_MRKT_DIV_CODE": "J",
                "FID_INPUT_ISCD": symbol,
                "FID_INPUT_DATE_1": start.strftime("%Y%m%d"),
                "FID_INPUT_DATE_2": end.strftime("%Y%m%d"),
                "FID_PERIOD_DIV_CODE": param_code,
                "FID_ORG_ADJ_PRC": "0",
            }
        else:
            assert ValueError(f"{base_market} is not valid value")

        if time_frame.endswith("m"):
            common_header = self.create_common_header(request_params=params)
            response = self.private_get_fetch_security_ohlcv_minute(self.extend(params))
        elif time_frame.endswith("D"):
            common_header = self.create_common_header(request_params=params)
            response = self.private_get_fetch_security_ohlcv_day(self.extend(params))
        elif time_frame.endswith("W"):
            common_header = self.create_common_header(request_params=params)
            response = self.private_get_fetch_security_ohlcv_week(self.extend(params))
        elif time_frame.endswith("M"):
            common_header = self.create_common_header(request_params=params)
            response = self.private_get_fetch_security_ohlcv_month(self.extend(params))
        elif time_frame.endswith("Y"):
            common_header = self.create_common_header(request_params=params)
            response = self.private_get_fetch_security_ohlcv_year(self.extend(params))

        common_response = self.get_common_response(response=response)
        if common_response.success != "0":
            return ksxt.models.KsxtHistoricalDataResponse(header=common_header, response=common_response, info=None)

        parsed_response = self.parser.parse_historical_data(
            response=response, symbol=symbol, start=start, end=end, base_market=base_market
        )

        return ksxt.models.KsxtHistoricalDataResponse(
            header=common_header, response=common_response, info=parsed_response
        )

    @RestExchange.check_token
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
        if base_market == "KRW":
            params = {
                "CANO": acc_num[:8],
                "ACNT_PRDT_CD": acc_num[-2:],
                "KRX_FWDG_ORD_ORGNO": "",
                "ORGN_ODNO": str(order_id),
                "RVSE_CNCL_DVSN_CD": "01",
                "ORD_DVSN": "00",
                "ORD_QTY": str(qty),
                "ORD_UNPR": str(price),
                "QTY_ALL_ORD_YN": "N",
            }
        else:
            assert ValueError(f"{base_market} is not valid value")

        common_header = self.create_common_header(request_params=params)
        response = self.private_post_send_modify_order(self.extend(params))

        common_response = self.get_common_response(response=response)
        if common_response.success != "0":
            return ksxt.models.KsxtModifyOrderResponse(header=common_header, response=common_response, info=None)

        parsed_info = self.parser.parse_modify_order(response=response, base_market=base_market)

        return ksxt.models.KsxtModifyOrderResponse(header=common_header, response=common_response, info=parsed_info)

    @RestExchange.check_token
    def cancel_order(
        self, acc_num: str, order_id: str, symbol: str | None = "", qty: float = 0, *args, base_market: str = "KRW"
    ) -> ksxt.models.KsxtCancelOrderResponse:
        if base_market == "KRW":
            params = {
                "CANO": acc_num[:8],
                "ACNT_PRDT_CD": acc_num[-2:],
                "KRX_FWDG_ORD_ORGNO": "",
                "ORGN_ODNO": str(order_id),
                "RVSE_CNCL_DVSN_CD": "02",
                "ORD_DVSN": "00",
                "ORD_QTY": str(qty),
                "ORD_UNPR": str(0),
                "QTY_ALL_ORD_YN": "N",
            }
        else:
            assert ValueError(f"{base_market} is not valid value")

        common_header = self.create_common_header(request_params=params)
        response = self.private_post_send_cancel_order(self.extend(params))

        common_response = self.get_common_response(response=response)
        if common_response.success != "0":
            return ksxt.models.KsxtCancelOrderResponse(header=common_header, response=common_response, info=None)

        parsed_info = self.parser.parse_cancel_order(response=response, base_market=base_market)

        return ksxt.models.KsxtCancelOrderResponse(header=common_header, response=common_response, info=parsed_info)

    @RestExchange.check_token
    def create_order(
        self,
        acc_num: str,
        symbol: str,
        ticket_type: Literal["EntryLong"] | Literal["EntryShort"] | Literal["ExitLong"] | Literal["ExitShort"],
        otype: Literal["limit"] | Literal["market"],
        price: float | None = 0,
        qty: float | None = 0,
        amount: float | None = 0,
        base_market: str = "KRW",
    ) -> ksxt.models.KsxtCreateOrderResponse:
        if otype.lower() == "limit":
            order_dvsn = "00"
        elif otype.lower() == "market":
            order_dvsn = "01"
        params = {
            "CANO": acc_num[:8],
            "ACNT_PRDT_CD": acc_num[-2:],
            "PDNO": symbol,
            "ORD_DVSN": order_dvsn,
            "ORD_QTY": str(qty),  # string type 으로 설정
            "ORD_UNPR": str(price),  # string type 으로 설정
        }

        common_header = self.create_common_header(request_params=params)

        if ticket_type == "EntryLong":
            response = self.private_post_send_order_entry(self.extend(params))
        elif ticket_type == "ExitLong":
            response = self.private_post_send_order_exit(self.extend(params))

        common_response = self.get_common_response(response=response)
        if common_response.success != "0":
            return ksxt.models.KsxtCreateOrderResponse(header=common_header, response=common_response, info=None)

        parsed_info = self.parser.parse_create_order(response=response, base_market=base_market)

        return ksxt.models.KsxtCreateOrderResponse(header=common_header, response=common_response, info=parsed_info)

    def get_market_code_in_feeder(self, symbol: str, base_market: str = "KRW"):
        if base_market == "KRW":
            return ""
        elif base_market == "USD":
            if symbol.upper() == "ALL":
                return "NASD"

            response = self.fetch_security(symbol=symbol, base_market=base_market)
            return response["exchange"]
        else:
            return ""

    def get_market_code_in_broker(self, symbol: str, base_market: str = "KRW"):
        if base_market == "KRW":
            return ""
        elif base_market == "USD":
            if symbol.upper() == "ALL":
                return "NASD"

            response = self.fetch_security(symbol=symbol, base_market=base_market)
            exname = response["exchange"]
            if exname == "NYS":
                return "NYSE"
            elif exname == "NAS":
                return "NASD"
            elif exname == "AMS":
                return "AMEX"
            else:
                return ""
        else:
            return ""
