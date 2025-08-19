from ksxt.api import Entry


class ImplicitAPI:

    # stock API methods

    # private methods

    # get requests
    private_get_fetch_balance = Entry("stock", "fetch_balance", {})
    private_get_fetch_cash = Entry("stock", "fetch_cash", {})
    private_get_fetch_orderbook = Entry("stock", "fetch_orderbook", {})
    private_get_fetch_security_info = Entry("stock", "fetch_security_info", {})
    private_get_fetch_ticker_price = Entry("stock", "fetch_ticker_price", {})
    private_get_fetch_index_ohlcv = Entry("stock", "fetch_index_ohlcv", {})
    private_get_fetch_security_ohlcv_day = Entry("stock", "fetch_security_ohlcv_day", {})
    private_get_fetch_security_ohlcv_minute = Entry("stock", "fetch_security_ohlcv_minute", {})
    private_get_fetch_security_ohlcv_month = Entry("stock", "fetch_security_ohlcv_month", {})
    private_get_fetch_security_ohlcv_week = Entry("stock", "fetch_security_ohlcv_week", {})
    private_get_fetch_security_ohlcv_year = Entry("stock", "fetch_security_ohlcv_year", {})
    # private_get_fetch_closed_order          = Entry('stock', 'fetch_closed_order', {})
    # private_get_fetch_opened_order          = Entry('stock', 'fetch_opened_order', {})
    # private_get_fetch_pnl                   = Entry('stock', 'fetch_pnl', {})
    # private_get_fetch_screener              = Entry('stock', 'fetch_screener', {})
    # private_get_fetch_screener_list         = Entry('stock', 'fetch_screener_list', {})

    # post requests
    private_post_send_modify_order = Entry("stock", "send_modify_order", {})
    private_post_send_cancel_order = Entry("stock", "send_cancel_order", {})
    private_post_send_order_entry = Entry("stock", "send_order_entry", {})
    private_post_send_order_exit = Entry("stock", "send_order_exit", {})
    private_post_send_order_loan_entry = Entry("stock", "send_order_loan_entry", {})
    private_post_send_order_loan_exit = Entry("stock", "send_order_loan_exit", {})

    # public methods

    # post requests
    public_post_generate_token = Entry("token", "generate_token", {})
    public_post_revoke_token = Entry("token", "revoke_token", {})
