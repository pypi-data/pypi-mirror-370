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
from functools import wraps
from math import isnan
import numpy as np


def update_invalid_nan(func):
    @wraps(func)
    def _decorate(*args, **kwargs):
        def _transfer(d):
            _func_list = [isnan, np.isnan]
            for _f in _func_list:
                if _f(d):
                    return 0
                return d
        data = func(*args, **kwargs)
        if isinstance(data, list):
            return [_transfer(d) for d in data]
        else:
            return _transfer(data)
    return _decorate