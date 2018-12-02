import sys
sys.path.append('../')
from unittest import TestCase
from nose.tools import nottest


import gltrader
from gltrader.trader import Trader
import gltrader.bittrex
from pprint import pprint as pp
from kit import dd

@nottest
def test_candles():
    trader = Trader()
    response = trader.api.get_candles("BTC-ETH", gltrader.bittrex.TICKINTERVAL_ONEMIN)
    pp(response)
    if response["success"]:
        assert True
    else:
        assert False
