entries = {
    "koreainvest": {
        "stock": {
            "private": {
                "get": [
                    "fetch_balance",
                    "fetch_cash",
                    "fetch_orderbook",
                    "fetch_security_info",
                    "fetch_ticker_price",
                    "fetch_index_ohlcv",
                    "fetch_security_ohlcv_day",
                    "fetch_security_ohlcv_minute",
                    "fetch_security_ohlcv_month",
                    "fetch_security_ohlcv_week",
                    "fetch_security_ohlcv_year",
                    "fetch_closed_order",
                    "fetch_opened_order",
                    "fetch_pnl",
                    "fetch_screener",
                    "fetch_screener_list",
                ],
                "post": [
                    "send_modify_order",
                    "send_cancel_order",
                    "send_order_entry",
                    "send_order_exit",
                    "send_order_loan_entry",
                    "send_order_loan_exit",
                ],
            },
            "public": {
                "post": [
                    "generate_token",
                    "revoke_token",
                ]
            },
        },
    },
    "websocket": {
        "stock": {
            "subscribe": {
                "ticker": ["subscribe_ticker"],
                "trade": ["subscribe_trade"],
                "orderbook": ["subscribe_orderbook"],
            }
        }
    },
}
