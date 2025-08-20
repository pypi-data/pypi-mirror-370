import numpy as np
import pandas as pd

from mgquant.utils import lazyimport
lazyimport.lazyimport(globals(), """
from supermind.data.main import command
from supermind.mod.mindgo.utils.recorder import log
from supermind.mod.mindgo.research import (
    bonus,
    valuation,
    balance,
    cashflow,
    income,
    profit_report,
    profit_forecast,
    operating,
    debtrepay,
    profit,
    growth,
    cashflow_sq,
    income_sq,
    profit_sq,
    growth_sq,
    asharevalue,
    ashareoperate,
    asharedebt,
    ashareprofit,
)
from supermind.mod.mindgo.research.research_api import (
    pd_Panel,
    normalize_symbol,
    get_security_info,
    get_price,
    get_candle_stick,
    get_all_trade_days,
    get_trade_days,
    get_last_trade_day,
    query,
    run_query,
    get_fundamentals,
    read_file,
    write_file,
    remove_file,
    superreload,
    notify_push,
    set_log_level,
    get_api_usage,
    upload_file,
    download_file,
)
from supermind.mod.stock.research_api import (
    get_price_future,
    get_candle_stick_future,
    get_futures_dominate,
    get_futures_info,
    get_future_code,
    get_all_securities,
    get_dividend_information,
    get_option_code,
    get_tick,
)
from supermind.mod.analyser.research_api import research_strategy
from supermind.mod.realtime.research_api import research_trade
from supermind.mod.tradeapi.api import (
    TradeAPI,
    TradeCredit,
    TradeFutures,
)
""")
del lazyimport

# hide all warning
import warnings
warnings.filterwarnings('ignore')
