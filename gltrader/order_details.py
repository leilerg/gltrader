import logging
log = logging.getLogger(__name__)

import builtins



SUPPORTED_EXCHANGES             = ["BITTREX"]
SUPPORTED_ORDER_TYPE            = ["MARKET", "LIMIT"]
SUPPORTED_ORDER_VALIDATION_TYPE = ["NONE", "STANDARD", "FULL"]

BITTREX_TIME_IN_EFFECT = ["GOOD_TIL_CANCELLED", "IMMEDIATE_OR_CANCEL", "FILL_OR_KILL"]
BITTREX_CONDITION_TYPE = ["NONE", "GREATER_THAN", "LESS_THAN",
                          "STOP_LOSS_FIXED", "STOP_LOSS_PERCENTAGE"] 




class OrderDetails(object):
    #===============================================================================================
    # This class contains all the details required for a given `Order()` and/or `Action()`.
    #
    # Some basic checks are performed to ensure integrity about the details.
    #===============================================================================================

    def __init__(self, orderDetailsDict, exchange="UNSUPPORTED_EXCHANGE"):
        #=====================================================================================
        # Initialize order details. The details are checked for completeness for a specific exchange
        # and default values are assigned if incomplete or missing. Invalid and/or missing values
        # for the critical details, e.g. a negative exhange rate, throw an exception.
        #
        # Inputs:
        # :orderDetailsDict: - Dictionary that contains all the order details expected for a given
        #                      exchange.
        # :exchange:         - String literal for the exchange (e.g. Bittrex, Binance, ...)
        #
        # To be fully specified, an order dictionary should contain at least the following keys:
        # - "marketName"     : String literal, e.g. "BTC-LTC" (:string:)
        # - "quantity"       : The quantity/amount of shitcoins to buy/sell (:float:)
        # - "rate"           : The exchange rate for the order (not needed for a market order) (:float:)
        # - "orderType"      : Type of order to place (:string:)
        #                      Valid options are:
        #                      * "LIMIT" (default)
        #                      * "MARKET"
        # - "balances"       : (dictionary) Various balances for a given `marketName`
        #   * "total"        : (double) Total ALT balance (sum of all ALT balances)
        #   * "available"    : (double) ALT balance available to trade
        #   * "reserved"     : (double) ALT balance reserved for trades (in exisitng orders)
        #   * "pending"      : (double) ALT pending balance (awaiting confirmations)
        #   * "avilableBTC"  : (double) BTC balance available to trade
        #
        # Additional keys, and the checks/conditions related to them, should be specified in the
        # related subclasses.
        #=====================================================================================
        self._isHealthy = False
        self._orderDetails = orderDetailsDict
        self._exchange = exchange

        # Sanity checks
        self.checkOrderDetails()



    def checkOrderDetails(self):
    #=====================================================================================
    # This method performs some basic checks that the order details are healthy.
    # 
    # Crititcal parameters raise exception errors, non-critical ones raise runtime warnings and get
    # initialized by the the defaults.
    # Critical vs non-critical will depend on the exchange, but some are (should be?) umiversal
    #=====================================================================================
        self._isHealthy = True
        # Check for supported exchange...
        if self._exchange not in SUPPORTED_EXCHANGES:
            self._isHealthy = False
            raise ValueError("CRITICAL ERROR - '" + str(self._exchange) +
                             "' is not a supported exchange") 
        # Check for trade market 
        if not self._orderDetails.get("marketName", False):
            self._isHealthy = False
            raise KeyError("CRITICAL ERROR - Missing `market` key in order_details[]")
        # Check for trade quantity
        if not self._orderDetails.get("quantity", False):
            self._isHealthy = False
            raise KeyError("CRITICAL ERROR - Missing or null `quantity` key in order details[]")
        # Check for trade fx rate
        # TO DO: The `rate` must now be a dictionary: Enhance checks to see if it contains all 
        # the important/key info 
        if not self._orderDetails.get("rate", False):
            self._isHealthy = False
            raise KeyError("CRITICAL ERROR - Missing or null `rate` key in order details[]")

        # Check for market balances
        if not self._orderDetails.get("balances", False):
            self._isHealthy = False
            raise KeyError("CRITICAL ERROR - Missing `balances` in order_details[]")

        # Check for BTC balances available for trade - At this point I know the key is in the dictionary
        if self._orderDetails["balances"].get("availableBTC", None) is None:
            self._isHealthy = False
            raise KeyError("CRITICAL ERROR - Missing `availableBTC` in order_details[\"balances\"]")
        
        # Check for total ALT balance - At this point I know the key is in the dictionary
        if self._orderDetails["balances"].get("total", None) is None:
            self._isHealthy = False
            raise KeyError("CRITICAL ERROR - Missing `total` in order_details[\"balances\"]")
        
        # Check for available ALT balance - At this point I know the key is in the dictionary
        if self._orderDetails["balances"].get("available", None) is None:
            self._isHealthy = False
            raise KeyError("CRITICAL ERROR - Missing `available` in order_details[\"balances\"]")
        
        # Check for reserved ALT balance - At this point I know the key is in the dictionary
        if self._orderDetails["balances"].get("reserved", None) is None:
            self._isHealthy = False
            raise KeyError("CRITICAL ERROR - Missing `reserved` in order_details[\"balances\"]")
        
        # Check for pending ALT balance - At this point I know the key is in the dictionary
        if self._orderDetails["balances"].get("pending", None) is None:
            self._isHealthy = False
            raise KeyError("CRITICAL ERROR - Missing `pending` in order_details[\"balances\"]")
        
        # Checks for the non-critical order details (defaults are set)
        if not self._orderDetails.get("orderType", False) or \
               self._orderDetails["orderType"] not in SUPPORTED_ORDER_TYPE:
            # Default to "LIMIT"
            self._orderDetails["orderType"] = "LIMIT"
            # And raise warning
            raise RuntimeWarning("WARNING - Missing or uknown `orderType` key in " +
                                 "Bittrex order details - Defaulting to `LIMIT`")

        # Checks for the order validation type - Default = "STANDARD"
        if not self._orderDetails.get("validationType", False) or \
               self._orderDetails["validationType"] not in SUPPORTED_ORDER_VALIDATION_TYPE:
            # Set default
            self._orderDetails["validationType"] = "STANDARD"
            # And raise warning
            raise RuntimeWarning("WARNING - Missing or unknown `validationType` key in " +
                                 "Order Details - Defaulting to `STANDARD`")

        # TO DO: Enhance checks - "balances" not required when performing a `FULL` validation of the order
        
        
    #===============================================================================================
    # These methods are expected to be available for every order, regardles of the exhange
    # Additionally, every exchange will have specific methods that must be defined as the new
    # exchange is added to the class.
    #===============================================================================================
    def marketName(self):
        #=====================================================================================
        # :return: (string literal) The market to trade (e.g. "BTC-LTC")
        #=====================================================================================
        return self._orderDetails["marketName"]

    def orderType(self):
        #=====================================================================================
        # :return: (string literal) The order type ("MARKET" or "LIMIT")
        #=====================================================================================
        return self._orderDetails["orderType"]

    def quantity(self):
        #=====================================================================================
        # :return: (double) The quantity of shitcoins to trade
        #=====================================================================================
        return self._orderDetails["quantity"]
        
    def rate(self):
        #=====================================================================================
        # :return: The exchange rate
        #=====================================================================================
        return self._orderDetails["rate"]

    def exchange(self):
        #=====================================================================================
        # :return: (string literal) The exchange where the order should be placed
        #=====================================================================================
        return self._exchange
    
    def validationType(self):
        #=====================================================================================
        # :return: (string literal) Order validation type
        #=====================================================================================
        return self._orderDetails["validationType"]
    
    def balances(self):
        #=====================================================================================
        # :return: (dict) Dictionary of all balances
        #=====================================================================================
        return self._orderDetails["balances"]

    def bitcoinBalance(self):
        #=====================================================================================
        # :return: (double) Available BTC balance for trading
        #=====================================================================================
        return self._orderDetails["balances"]["balanceBTC"]

    def totalBalance(self):
        #=====================================================================================
        # :return: (double) Total ALT balance (sum of all ALT balances)
        #=====================================================================================
        return self._orderDetails["balances"]["total"]
    
    def availableBalance(self):
        #=====================================================================================
        # :return: (double) Available ALT balance for trading
        #=====================================================================================
        return self._orderDetails["balances"]["available"]
    
    def pendingBalance(self):
        #=====================================================================================
        # :return: (double) Pending ALT balance (awaiting confirmations)
        #=====================================================================================
        return self._orderDetails["balances"]["pending"]
    
    def reservedBalance(self):
        #=====================================================================================
        # :return: (double) Reserved ALT balance (reserved in other trades)
        #=====================================================================================
        return self._orderDetails["balances"]["reserved"]
    
    def isHealthy(self):
        #=====================================================================================
        # :return: Order details status
        #=====================================================================================
        return self._isHealthy


    def pop(self, key):
        #=====================================================================================
        # Input:
        # - key : (String literal) - The dictionary key
        # 
        # :return: orderDetails[key] and removes `key` from dictionary
        # (Equivalent to dictionary.pop(key))
        #=====================================================================================
        return self._orderDetails.pop(key)
        
    
    


class BittrexOrderDetails(OrderDetails):
    #===============================================================================================
    # `OrderDetails` sub-class specific for Bittrex.
    #
    # To be fully specified, a Bittrex order dictionary should contain the following keys:
    # - "marketName"     : String literal, e.g. "BTC-LTC" (:string:)
    # - "quantity"       : The quantity/amount of shitcoins to buy/sell (:float:)
    # - "rate"           : The exchange rate for the order (not needed for a market order) (:float:)
    # - "orderType"      : Type of order to place (:string:)
    #                      Valid options are:
    #                      * "LIMIT" (default)
    #                      * "MARKET"
    # - "timeInEffect"   : The time an order should continue to be valid/active (:string:)
    #                      Valid options are:
    #                      * "GOOD_TIL_CANCELLED" (default)
    #                      * "IMMEDIATE_OR_CANCEL"
    #                      * "FILL_OR_KILL"
    # - "conditionType"  : Conditions on the order? (:string:)
    #                      Valid options are:
    #                      * "NONE" (default)
    #                      * "GREATER_THAN"
    #                      * "LESS_THAN"
    #                      * "STOP_LOSS_FIXED"
    #                      * "STOP_LOSS_PERCENTAGE"
    # - "target"         : Used in conjuction with `condition_type` (float)
    #
    # The checks are specific to Bittrex
    #===============================================================================================

    _exchange = "BITTREX"

    def __init__(self, orderDetailsDict):
        # Initialize class
        super().__init__(orderDetailsDict, exchange = self._exchange)

        # Perform sanity checks
        self.checkOrderDetails()


    def checkOrderDetails(self):
        #=====================================================================================
        # This method performs some basic checks that the order details are healthy.
        # 
        # For some (non critical) paraments it will set defaults, but for the more critical ones it
        # will raise an exception.
        #=====================================================================================
        # Base class checks
        super().checkOrderDetails()

        # Checks non-critical details - Time In Effect - Default: GOOD_TIL_CANCELLED
        if not self._orderDetails.get("timeInEffect", False) or \
               self._orderDetails["timeInEffect"] not in BITTREX_TIME_IN_EFFECT:
            # Default to "GOOD_TIL_CANCELLED"
            self._orderDetails["orderType"] = "GOOD_TIL_CANCELLED"
            # And raise warning
            raise RuntimeWarning("WARNING - Missing or unknown `timeInEffect` key in " +
                                 "Bittrex order details - Defaulting to `GOOD_TIL_CANCELLED`")

        # Checks non-critical details - Condition Type - Default: NONE
        if not self._orderDetails.get("conditionType", False) or \
               self._orderDetails["conditionType"] not in BITTREX_CONDITION_TYPE:
            # Default to `NONE`
            self._orderDetails["conditionType"] = "NONE"
            # Raise warning
            raise RuntimeWarning("WARNING - Missing or unknown `conditionType` key in, " +
                                 "Bittrex order details - Defaulting to `NONE`")

        # Checks non-critical details - Target - Default: 0.
        if "target" not in self._orderDetails:
            # Default to zero
            self._orderDetails["target"] = 0.
            # Rasie warning
            raise RuntimeWarning("WARNING - Missing `target` key in " +
                                 "Bittrex order details - Defaulting to zero.")
        elif self._orderDetails["target"] < 0.:
            # Default to zero
            self._orderDetails["target"] = 0.
            # Rasie warning
            raise RuntimeWarning("WARNING - Invalid `target` key value in " +
                                 "Bittrex order details - Defaulting to zero.")

        
    def timeInEffect(self):
        #=====================================================================================
        # :return: The time in effect for the order
        #=====================================================================================
        return self._orderDetails["timeInEffect"]
        
    def conditionType(self):
        #=====================================================================================
        # :return: The condition for the order
        #=====================================================================================
        return self._orderDetails["conditionType"]
        
    def target(self):
        #=====================================================================================
        # :return: The target used in conjunction with the `conditionType`
        #=====================================================================================
        return self._orderDetails["target"]
        



    #===============================================================================================
    # ADDITIONAL CHECKS - NOT FULLY IMPLEMENTED!!
    #
    # There should be various additional sanity checks for each of the order detail parameters...
    # Examples: the numbers are numbers, the strings are strings, the numbers are not negative, and
    # so on.
    #===============================================================================================

    
    # def parseAmount(self, amt):
    #     #=======================================================================
    #     # This was previously in order.py
    #     #
    #     # Makes sure amount is within range allowed
    #     # 
    #     # :param amt: (Float) The amount passed into the object
    #     # :returns: (Float/Boolean) The validated amount or False if invalid
    #     #=======================================================================

    #     self.minTrade = self.market.config["min_trade_amount"]
    #     self.maxTrade = self.market.config["max_trade_amount"]
    #     self.maxTradeTot = self.market.config["max_trade_total"]

    #     if (self.market.name in self.market.config):
    #         if ("min_trade_amount" in self.market.config):
    #             self.minTrade = self.market.config["min_trade_amount"]
    #         if ("max_trade_amount" in self.market.config):
    #             self.maxTrade = self.market.config["max_trade_amount"]
    #         if ("max_trade_total" in self.market.config):
    #             self.maxTradeTot = self.market.config["max_trade_total"]

    #     if (amt <= self.maxTrade and amt >= self.minTrade):
    #         return amt
    #     else:
    #         Error("trade amount out of range", self.market)
    #         log.debug("Max Trade: " + str(self.maxTrade) + "\n" +
    #                   "Min Trade: " + str(self.minTrade))
    #         return False
