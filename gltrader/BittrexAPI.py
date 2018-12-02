"""
	Bittrex wrapper 
	
	Some of the API calls are currently only available for v1.1 of the API
	whilst others are only available for v2.0. 
	
	This wrapper allows access to all of them in a transparent way. 
	
	The general rule is that if v2.0 is available, it will be used. Else, v1.1.
	
	It uses the bittrex API from:	https://github.com/ericsomdahl/python-bittrex
"""



from .bittrex import Bittrex

BUY_ORDERBOOK = 'buy'
SELL_ORDERBOOK = 'sell'
BOTH_ORDERBOOK = 'both'



class BittrexAPI(object):

	#===========================================================================
	# API Methods definitions
	# 
	# Default call: API v2.0
	# If not available, v1.1
	#===========================================================================

	#number of times the API has been called
	#ApiCalls = 0
	
	def __init__(self, api_key, api_secret, calls_per_sec=1):
		#Initialize two APIs, one for v1.1 and one for v2.0
		self.BittrexAPI_V1_1 = Bittrex(api_key, api_secret, api_version="v1.1", calls_per_second=calls_per_sec)
		self.BittrexAPI_V2_0 = Bittrex(api_key, api_secret, api_version="v2.0", calls_per_second=calls_per_sec)
		self.ApiCalls = 0



	def get_markets(self):
		#=======================================================================
		# Used to get the open and available trading markets
		# at Bittrex along with other meta data.
		# 
		# Example ::
		#     {'success': True,
		#      'message': '',
		#      'result': [ {'MarketCurrency': 'LTC',
		#                   'BaseCurrency': 'BTC',
		#                   'MarketCurrencyLong': 'Litecoin',
		#                   'BaseCurrencyLong': 'Bitcoin',
		#                   'MinTradeSize': 1e-08,
		#                   'MarketName': 'BTC-LTC',
		#                   'IsActive': True,
		#                   'Created': '2014-02-13T00:00:00',
		#                   'Notice': None,
		#                   'IsSponsored': None,
		#                   'LogoUrl': 'https://i.imgur.com/R29q3dD.png'},
		#                   ...
		#                 ]
		#     }
		#
		# :return: Available market info in JSON
		# :rtype : dict
		#=======================================================================
		self.ApiCalls = self.ApiCalls + 1
		return self.BittrexAPI_V2_0.get_markets()


	def get_currencies(self):
		#=============================================================================
		# Used to get all supported currencies at Bittrex
		# along with other meta data.
		# 
		# :return: Supported currencies info in JSON
		# :rtype : dict
		#=============================================================================
		self.ApiCalls = self.ApiCalls + 1
		return self.BittrexAPI_V2_0.get_currencies()


	def get_ticker(self, market):
		#=======================================================================
		# Used to get the current tick values for a market.
		# 
		# :param market: String literal for the market (ex: BTC-LTC)
		# :type market: str
		# :return: Current values for given market in JSON
		# :rtype : dict
		#=======================================================================
		self.ApiCalls = self.ApiCalls + 1
		return self.BittrexAPI_V1_1.get_ticker(market)



	def get_market_summaries(self):
		#=======================================================================
		# Used to get the last 24 hour summary of all active exchanges
		# 
		# :return: Summaries of active exchanges in JSON
		# :rtype : dict
		#=======================================================================
		self.ApiCalls = self.ApiCalls + 1
		return self.BittrexAPI_V2_0.get_market_summaries()



	def get_marketsummary(self, market):
		#=======================================================================
		# Used to get the last 24 hour summary of all active
		# exchanges in specific coin
		# 
		# :param market: String literal for the market(ex: BTC-XRP)
		# :type market: str
		# :return: Summaries of active exchanges of a coin in JSON
		# :rtype : dict
		#=======================================================================
		self.ApiCalls = self.ApiCalls + 1
		return self.BittrexAPI_V2_0.get_markersummary(market)


	def get_orderbook(self, market, depth_type=BOTH_ORDERBOOK):
		#=======================================================================
		# Used to get retrieve the orderbook for a given market.
		# The depth_type parameter is IGNORED under v2.0 and both orderbooks are aleways returned
		# 
		# :param market: String literal for the market (ex: BTC-LTC)
		# :type market: str
		# :param depth_type: buy, sell or both to identify the type of
		#     orderbook to return.
		#     Use constants BUY_ORDERBOOK, SELL_ORDERBOOK, BOTH_ORDERBOOK
		# :type depth_type: str
		# :return: Orderbook of market in JSON
		# :rtype : dict
		#=======================================================================
		self.ApiCalls = self.ApiCalls + 1
		return self.BittrexAPI_V2_0.get_orderbook(market, depth_type)


	def get_market_history(self, market):
		#=======================================================================
		# Used to retrieve the latest trades that have occurred for a
		# specific market.
		# 
		# Example ::
		#     {'success': True,
		#     'message': '',
		#     'result': [ {'Id': 5625015,
		#                  'TimeStamp': '2017-08-31T01:29:50.427',
		#                  'Quantity': 7.31008193,
		#                  'Price': 0.00177639,
		#                  'Total': 0.01298555,
		#                  'FillType': 'FILL',
		#                  'OrderType': 'BUY'},
		#                  ...
		#                ]
		#     }
		# :param market: String literal for the market (ex: BTC-LTC)
		# :type market: str
		# :return: Market history in JSON
		# :rtype : dict
		#=======================================================================
		self.ApiCalls = self.ApiCalls + 1
		return self.BittrexAPI_V2_0.get_market_history(market)


	def buy_limit(self, market, quantity, rate):
		#=======================================================================
		# Used to place a buy order in a specific market. Use buylimit to place
		# limit orders Make sure you have the proper permissions set on your
		# API keys for this call to work
		# 
		# :param market: String literal for the market (ex: BTC-LTC)
		# :type market: str
		# :param quantity: The amount to purchase
		# :type quantity: float
		# :param rate: The rate at which to place the order.
		#     This is not needed for market orders
		# :type rate: float
		# :return:
		# :rtype : dict
		#=======================================================================
		self.ApiCalls = self.ApiCalls + 1
		return self.BittrexAPI_V1_1.buy_limit(market, quantity, rate)


	def sell_limit(self, market, quantity, rate):
		#=======================================================================
		# Used to place a sell order in a specific market. Use selllimit to place
		# limit orders Make sure you have the proper permissions set on your
		# API keys for this call to work
		# 
		# :param market: String literal for the market (ex: BTC-LTC)
		# :type market: str
		# :param quantity: The amount to purchase
		# :type quantity: float
		# :param rate: The rate at which to place the order.
		#     This is not needed for market orders
		# :type rate: float
		# :return:
		# :rtype : dict
		#=======================================================================
		self.ApiCalls = self.ApiCalls + 1
		return self.BittrexAPI_V1_1.sell_limit(market, quantity, rate)


	def cancel(self, uuid):
		#=======================================================================
		# Used to cancel a buy or sell order
		# 
		# :param uuid: uuid of buy or sell order
		# :type uuid: str
		# :return:
		# :rtype : dict
		#=======================================================================
		self.ApiCalls = self.ApiCalls + 1
		return self.BittrexAPI_V2_0.cancel(uuid)


	def get_open_orders(self, market=None):
		#=======================================================================
		# Get all orders that you currently have opened.
		# A specific market can be requested.
		# 
		# :param market: String literal for the market (ie. BTC-LTC)
		# :type market: str
		# :return: Open orders info in JSON
		# :rtype : dict
		#=======================================================================
		self.ApiCalls = self.ApiCalls + 1
		return self.BittrexAPI_V2_0.get_open_orders(market)


	def get_balances(self):
		#=======================================================================
		# Used to retrieve all balances from your account.
		# 
		# Example ::
		#     {'success': True,
		#      'message': '',
		#      'result': [ {'Currency': '1ST',
		#                   'Balance': 10.0,
		#                   'Available': 10.0,
		#                   'Pending': 0.0,
		#                   'CryptoAddress': None},
		#                   ...
		#                 ]
		#     }
		# :return: Balances info in JSON
		# :rtype : dict
		#=======================================================================
		self.ApiCalls = self.ApiCalls + 1
		return self.BittrexAPI_V2_0.get_balances()


	def get_balance(self, currency):
		#=======================================================================
		# Used to retrieve the balance from your account for a specific currency
		# 
		# Example ::
		#     {'success': True,
		#      'message': '',
		#      'result': {'Currency': '1ST',
		#                 'Balance': 10.0,
		#                 'Available': 10.0,
		#                 'Pending': 0.0,
		#                 'CryptoAddress': None}
		#     }
		# :param currency: String literal for the currency (ex: LTC)
		# :type currency: str
		# :return: Balance info in JSON
		# :rtype : dict
		#=======================================================================
		self.ApiCalls = self.ApiCalls + 1
		return self.BittrexAPI_V2_0.get_balance(currency)


	def get_deposit_address(self, currency):
		#=======================================================================
		# Used to generate or retrieve an address for a specific currency
		# 
		# :param currency: String literal for the currency (ie. BTC)
		# :type currency: str
		# :return: Address info in JSON
		# :rtype : dict
		#=======================================================================
		self.ApiCalls = self.ApiCalls + 1
		return self.BittrexAPI_V2_0.get_deposit_address(currency)


	def withdraw(self, currency, quantity, address):
		#=======================================================================
		# Used to withdraw funds from your account
		# 
		# :param currency: String literal for the currency (ie. BTC)
		# :type currency: str
		# :param quantity: The quantity of coins to withdraw
		# :type quantity: float
		# :param address: The address where to send the funds.
		# :type address: str
		# :return:
		# :rtype : dict
		#=======================================================================
		self.ApiCalls = self.ApiCalls + 1
		return self.BittrexAPI_V2_0.withdraw(currency, quantity, address)


	def get_order_history(self, market=None):
		#=======================================================================
		# Used to retrieve order trade history of account
		# 
		# :param market: optional a string literal for the market (ie. BTC-LTC).
		#     If omitted, will return for all markets
		# :type market: str
		# :return: order history in JSON
		# :rtype : dict
		#=======================================================================
		self.ApiCalls = self.ApiCalls + 1
		return self.BittrexAPI_V2_0.get_order_history(market)


	def get_order(self, uuid):
		#=======================================================================
		# Used to get details of buy or sell order
		# 
		# :param uuid: uuid of buy or sell order
		# :type uuid: str
		# :return:
		# :rtype : dict
		#=======================================================================
		self.ApiCalls = self.ApiCalls + 1
		return self.BittrexAPI_V2_0.get_order(uuid)


	def get_withdrawal_history(self, currency=None):
		#=======================================================================
		# Used to view your history of withdrawals
		# 
		# :param currency: String literal for the currency (ie. BTC)
		# :type currency: str
		# :return: withdrawal history in JSON
		# :rtype : dict
		#=======================================================================
		self.ApiCalls = self.ApiCalls + 1
		return self.BittrexAPI_V2_0.get_withdrawal_historu(currency)


	def get_deposit_history(self, currency=None):
		#=======================================================================
		# Used to view your history of deposits
		# 
		# :param currency: String literal for the currency (ie. BTC)
		# :type currency: str
		# :return: deposit history in JSON
		# :rtype : dict
		#=======================================================================
		self.ApiCalls = self.ApiCalls + 1
		return self.BittrexAPI_V2_0.get_deposit_history(currency)


	def list_markets_by_currency(self, currency):
		#=======================================================================
		# Helper function to see which markets exist for a currency.
		# 
		# Example ::
		#     >>> Bittrex(None, None).list_markets_by_currency('LTC')
		#     ['BTC-LTC', 'ETH-LTC', 'USDT-LTC']
		# :param currency: String literal for the currency (ex: LTC)
		# :type currency: str
		# :return: List of markets that the currency appears in
		# :rtype: list
		#=======================================================================
		self.ApiCalls = self.ApiCalls + 1
		return [market['MarketName'] for market in self.BittrexAPI_V1_1.get_markets()['result']
		        if market['MarketName'].lower().endswith(currency.lower())]


	def list_bitcoin_markets(self):
		#=======================================================================
		# Helper function to see all markets trading against Bitcoin.
		# 
		# Example ::
		#     >>> Bittrex(None, None).list_markets_by_currency('LTC')
		#     ['BTC-LTC', 'ETH-LTC', 'USDT-LTC']
		# :param currency: String literal for the currency (ex: LTC)
		# :type currency: str
		# :return: List of markets that the currency appears in
		# :rtype: list
		#=======================================================================
		self.ApiCalls = self.ApiCalls + 1
		return [market['MarketName'] for market in self.BittrexAPI_V1_1.get_markets()['result']
		        if market['MarketName'].lower().startswith("btc")]


	def get_wallet_health(self):
		#=======================================================================
		# Used to view wallet health
		# 
		# :return:
		#=======================================================================
		self.ApiCalls = self.ApiCalls + 1
		return self.BittrexAPI_V2_0.get_wallet_health()


	def get_balance_distribution(self):
		#=======================================================================
		# Used to view balance distibution
		# Endpoints:
		# 1.1 NO Equivalent
		# 2.0 /pub/Currency/GetBalanceDistribution
		# :return:
		#=======================================================================
		self.ApiCalls = self.ApiCalls + 1
		return self.BittrexAPI_V2_0.get_balance_distribution()


	def get_pending_withdrawals(self, currency=None):
		#=======================================================================
		# Used to view your pending withdrawls
		# 
		# :param currency: String literal for the currency (ie. BTC)
		# :type currency: str
		# :return: pending widthdrawls in JSON
		# :rtype : list
		#=======================================================================
		self.ApiCalls = self.ApiCalls + 1
		return self.BittrexAPI_V2_0.get_pending_withdrawals(currency)


	def get_pending_deposits(self, currency=None):
		#=======================================================================
		# Used to view your pending deposits
		# 
		# :param currency: String literal for the currency (ie. BTC)
		# :type currency: str
		# :return: pending deposits in JSON
		# :rtype : list
		#=======================================================================
		self.ApiCalls = self.ApiCalls + 1
		return self.BittrexAPI_V2_0.get_pendimg_deposits(currency)


	def generate_deposit_address(self, currency):
		#=======================================================================
		# Generate a deposit address for the specified currency
		# 
		# :param currency: String literal for the currency (ie. BTC)
		# :type currency: str
		# :return: result of creation operation
		# :rtype : dict
		#=======================================================================
		self.ApiCalls = self.ApiCalls + 1
		
		return self.BittrexAPI_V2_0.generate_depoit_address(currency)


	def trade_sell(self, market=None, order_type=None, quantity=None, rate=None, time_in_effect=None,
                   condition_type=None, target=0.0):
		#=======================================================================
		# Enter a sell order into the book
		# 
		# :param market: String literal for the market (ex: BTC-LTC)
		# :type market: str
		# :param order_type: ORDERTYPE_LIMIT = 'LIMIT' or ORDERTYPE_MARKET = 'MARKET'
		# :type order_type: str
		# :param quantity: The amount to purchase
		# :type quantity: float
		# :param rate: The rate at which to place the order.
		#     This is not needed for market orders
		# :type rate: float
		# :param time_in_effect: TIMEINEFFECT_GOOD_TIL_CANCELLED = 'GOOD_TIL_CANCELLED',
		#         TIMEINEFFECT_IMMEDIATE_OR_CANCEL = 'IMMEDIATE_OR_CANCEL', or TIMEINEFFECT_FILL_OR_KILL = 'FILL_OR_KILL'
		# :type time_in_effect: str
		# :param condition_type: CONDITIONTYPE_NONE = 'NONE', CONDITIONTYPE_GREATER_THAN = 'GREATER_THAN',
		#         CONDITIONTYPE_LESS_THAN = 'LESS_THAN', CONDITIONTYPE_STOP_LOSS_FIXED = 'STOP_LOSS_FIXED',
		#         CONDITIONTYPE_STOP_LOSS_PERCENTAGE = 'STOP_LOSS_PERCENTAGE'
		# :type condition_type: str
		# :param target: used in conjunction with condition_type
		# :type target: float
		# :return:
		#=======================================================================
		self.ApiCalls = self.ApiCalls + 1
		
		return self.BittrexAPI_V2_0.trade_sell(market, order_type, quantity, rate, time_in_effect, condition_type, target)


	def trade_buy(self, market=None, order_type=None, quantity=None, rate=None, time_in_effect=None,
                  condition_type=None, target=0.0):
        #=======================================================================
        # Enter a buy order into the book
        #
        # :param market: String literal for the market (ex: BTC-LTC)
        # :type market: str
        # :param order_type: ORDERTYPE_LIMIT = 'LIMIT' or ORDERTYPE_MARKET = 'MARKET'
        # :type order_type: str
        # :param quantity: The amount to purchase
        # :type quantity: float
        # :param rate: The rate at which to place the order.
        #     This is not needed for market orders
        # :type rate: float
        # :param time_in_effect: TIMEINEFFECT_GOOD_TIL_CANCELLED = 'GOOD_TIL_CANCELLED',
        #         TIMEINEFFECT_IMMEDIATE_OR_CANCEL = 'IMMEDIATE_OR_CANCEL', or TIMEINEFFECT_FILL_OR_KILL = 'FILL_OR_KILL'
        # :type time_in_effect: str
        # :param condition_type: CONDITIONTYPE_NONE = 'NONE', CONDITIONTYPE_GREATER_THAN = 'GREATER_THAN',
        #         CONDITIONTYPE_LESS_THAN = 'LESS_THAN', CONDITIONTYPE_STOP_LOSS_FIXED = 'STOP_LOSS_FIXED',
        #         CONDITIONTYPE_STOP_LOSS_PERCENTAGE = 'STOP_LOSS_PERCENTAGE'
        # :type condition_type: str
        # :param target: used in conjunction with condition_type
        # :type target: float
        # :return:
        #=======================================================================
		self.ApiCalls = self.ApiCalls + 1
		
		return self.BittrexAPI_V2_0.trade_buy(market, order_type, quantity, rate, time_in_effect, condition_type, target)


	def get_candles(self, market, tick_interval):
        #=======================================================================
        # Used to get all tick candle for a market.
        #
        # Example  ::
        #     { success: true,
        #       message: '',
        #       result:
        #        [ { O: 421.20630125,
        #            H: 424.03951276,
        #            L: 421.20630125,
        #            C: 421.20630125,
        #            V: 0.05187504,
        #            T: '2016-04-08T00:00:00',
        #            BV: 21.87921187 },
        #          { O: 420.206,
        #            H: 420.206,
        #            L: 416.78743422,
        #            C: 416.78743422,
        #            V: 2.42281573,
        #            T: '2016-04-09T00:00:00',
        #            BV: 1012.63286332 }]
        #     }
        #
        # :return: Available tick candle in JSON
        # :rtype: dict
        #
        #=======================================================================
		self.ApiCalls = self.ApiCalls + 1
		
		return self.BittrexAPI_V2_0.get_candles(market, tick_interval)


	def get_latest_candle(self, market, tick_interval):
        #=======================================================================
        # Used to get the latest candle for the market.
		# 
        # Example ::
        #     { success: true,
        #       message: '',
        #       result:
        #       [ {   O : 0.00350397,
        #             H : 0.00351000,
        #             L : 0.00350000,
        #             C : 0.00350350,
        #             V : 1326.42643480,
        #             T : 2017-11-03T03:18:00,
        #             BV: 4.64416189 } ]
        #     }
        #
        # :return: Available latest tick candle in JSON
        # :rtype: dict
        #
        #=======================================================================
		self.ApiCalls = self.ApiCalls + 1
		
		return self.BittrexAPI_V2_0.get_latest_candle(market, tick_interval)


	def getApiCalls(self):
		return self.ApiCalls

