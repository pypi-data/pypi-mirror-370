from typing import Union
from ksxt.market.krx.kospi import Kospi, KospiItem
from ksxt.market.krx.kosdaq import Kosdaq, KosdaqItem
from ksxt.market.us.nasdaq import Nasdaq, NasdaqItem
from ksxt.market.us.nyse import Nyse, NyseItem
from ksxt.market.us.amex import Amex, AmexItem

MARKETS = {
    "kospi": Kospi,
    "kosdaq": Kosdaq,
    "nyse": Nyse,
    "nasdaq": Nasdaq,
    "amex": Amex,
}

MARKET_TYPE = Union[Kospi, Kosdaq, Nyse, Nasdaq, Amex]
MARKET_ITEM_TYPE = Union[KospiItem, KosdaqItem, NyseItem, NasdaqItem, AmexItem]
