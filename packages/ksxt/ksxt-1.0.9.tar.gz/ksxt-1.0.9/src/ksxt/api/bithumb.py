from ksxt.api import Entry


class ImplicitAPI:

    # stock API methods

    # public methods

    # get requests
    public_get_fetch_markets = Entry("stock", "fetch_markets", {})
    public_get_fetch_security_ohlcv_minute = Entry("stock", "fetch_security_ohlcv_minute", {})
    public_get_fetch_security_ohlcv_day = Entry("stock", "fetch_security_ohlcv_day", {})
    public_get_fetch_security_ohlcv_week = Entry("stock", "fetch_security_ohlcv_week", {})
    public_get_fetch_security_ohlcv_month = Entry("stock", "fetch_security_ohlcv_month", {})
    public_get_fetch_ticker_price = Entry("stock", "fetch_ticker_price", {})
    public_get_fetch_tickers_price = Entry("stock", "fetch_tickers_price", {})
    public_get_fetch_orderbook = Entry("stock", "fetch_orderbook", {})
    public_get_fetch_orderbooks = Entry("stock", "fetch_orderbooks", {})
    public_get_fetch_security_info = Entry("stock", "fetch_security_info", {})

    # private methods

    # get requests
    private_get_fetch_balance = Entry("stock", "fetch_balance", {})
    private_get_fetch_cash = Entry("stock", "fetch_cash", {})
    private_get_fetch_trade_fee = Entry("stock", "fetch_trade_fee", {})
    private_get_fetch_opened_order = Entry("stock", "fetch_opened_order", {})
    private_get_fetch_opened_order_detail = Entry("stock", "fetch_opened_order_detail", {})
    private_get_fetch_closed_order = Entry("stock", "fetch_closed_order", {})
    private_get_fetch_closed_order_detail = Entry("stock", "fetch_closed_order_detail", {})
    private_get_fetch_withdrawal_history = Entry("stock", "fetch_withdrawal_history", {})
    private_get_fetch_deposit_history = Entry("stock", "fetch_deposit_history", {})

    # post requests
    private_post_send_order_entry = Entry("stock", "send_order_entry", {})
    private_post_send_order_entry_market = Entry("stock", "send_order_entry_market", {})
    private_post_send_order_exit = Entry("stock", "send_order_exit", {})
    private_post_send_order_exit_market = Entry("stock", "send_order_exit_market", {})

    # delete requests
    private_delete_send_cancel_order = Entry("stock", "send_cancel_order", {})
