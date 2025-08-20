# @Author: xiewenqian <int>
# @Date:   2022-12-22T10:10:33+08:00
# @Email:  wixb50@gmail.com
# @Last modified by:   int
# @Last modified time: 2022-12-22T16:27:14+08:00


import pandas as pd
try:
    pd_Panel = pd.Panel
except AttributeError:
    from .panel import pd_Panel


__all__ = [
    'pd_Panel',
]
