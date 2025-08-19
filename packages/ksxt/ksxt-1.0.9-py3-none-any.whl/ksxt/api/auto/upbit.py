entries = {
    "upbit": {
        "stock": {
            "public": {
                "get": [
                    "fetch_markets",
                    "fetch_security_ohlcv_minute",
                    "fetch_security_ohlcv_day",
                    "fetch_security_ohlcv_week",
                    "fetch_security_ohlcv_month",
                    "fetch_ticker_price",
                    "fetch_tickers_price",
                    "fetch_orderbook",
                    "fetch_orderbooks",
                ]
            },
            "private": {
                "get": [
                    "fetch_balance",
                    "fetch_cash",
                    "fetch_security_info",
                    "fetch_trade_fee",
                    "fetch_closed_order_detail",
                    "fetch_opened_order_detail",
                    "fetch_opened_order",
                    "fetch_closed_order",
                    "fetch_withdrawal_history",
                    "fetch_deposit_history",
                ],
                "post": ["send_order_entry", "send_order_entry_market", "send_order_exit", "send_order_exit_market"],
                "delete": ["send_cancel_order"],
            },
        },
        "websocket": {
            "public": ["subscribe_ticker", "subscribe_trade", "subscribe_orderbook", "subscribe_order"],
            "private": ["subscribe_ticker", "subscribe_trade"],
        },
    }
}
