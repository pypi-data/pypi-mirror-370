# @Author: yangzijiang <int>
# @Date:   2018-05-07T14:10:33+08:00
# @Email:  wixb50@gmail.com
# @Last modified by:   int
# @Last modified time: 2018-05-07T16:27:14+08:00


__config__ = {
    # 开启/关闭 股票 T+1， 默认开启
    "stock_t1": True,
    # 是否开启信号模式
    "signal": False,
    # 启用的回测引擎，目前支持 `current_bar` (当前Bar收盘价撮合) 和 `next_bar` (下一个Bar开盘价撮合)
    "matching_type": "current_bar",
    # 设置滑点
    "slippage": 0,
    # 设置手续费乘数，默认为1
    "commission_multiplier": 1,
    # price_limit: 在处于涨跌停时，无法买进/卖出，默认开启【在 Signal 模式下，不再禁止买进/卖出，如果开启，则给出警告提示。】
    "price_limit": True,
    # liquidity_limit: 当对手盘没有流动性的时候，无法买进/卖出，默认关闭
    "liquidity_limit": False,
    # 是否有成交量限制
    "volume_limit": True,
    # 按照当前成交量的百分比进行撮合
    "volume_percent": 0.25,
}


def load_mod():
    from .mod import StockPaperMod
    return StockPaperMod()
