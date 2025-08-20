# -*- coding: utf-8 -*-
#
# Copyright 2017 MindGo, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from mgquant.const import DEFAULT_ACCOUNT_TYPE

from .commission import StockCommission, FutureCommission, OptionCommission
from .slippage import StockPriceSlippage, FuturePriceSlippage, OptionPriceSlippage
from .tax import StockTax, FutureTax, OptionTax


class CommissionDecider(object):
    def __init__(self, multiplier):
        self.deciders = dict()
        self.deciders[DEFAULT_ACCOUNT_TYPE.STOCK.name] = StockCommission(multiplier)
        self.deciders[DEFAULT_ACCOUNT_TYPE.FUTURE.name] = FutureCommission(multiplier)
        self.deciders[DEFAULT_ACCOUNT_TYPE.OPTION.name] = OptionCommission()

    def get_commission(self, account_type, trade):
        return self.deciders[account_type].get_commission(trade)


class SlippageDecider(object):
    def __init__(self, rate):
        self.deciders = dict()
        self.deciders[DEFAULT_ACCOUNT_TYPE.STOCK.name] = StockPriceSlippage(rate)
        self.deciders[DEFAULT_ACCOUNT_TYPE.FUTURE.name] = FuturePriceSlippage(rate)
        self.deciders[DEFAULT_ACCOUNT_TYPE.OPTION.name] = OptionPriceSlippage(rate)

    def get_trade_price(self, account_type, side, price):
        return self.deciders[account_type].get_trade_price(side, price)

    def update_slippage(self, account_type, slippage_style):
        self.deciders[account_type] = slippage_style


class TaxDecider(object):
    def __init__(self, rate=None):
        self.deciders = dict()
        self.deciders[DEFAULT_ACCOUNT_TYPE.STOCK.name] = StockTax(rate)
        self.deciders[DEFAULT_ACCOUNT_TYPE.BENCHMARK.name] = StockTax(rate)
        self.deciders[DEFAULT_ACCOUNT_TYPE.FUTURE.name] = FutureTax(rate)
        self.deciders[DEFAULT_ACCOUNT_TYPE.OPTION.name] = OptionTax(rate)

    def get_tax(self, account_type, trade):
        return self.deciders[account_type].get_tax(trade)
