from kivy.app import App
from .notification import *

import logging
log = logging.getLogger(__name__)



class Order(object):
    #===========================================================================
    # *** REVISION REQUIRED ***
    # 
    # Orders are the objects which interface with API trades.  
    # They implement the last-defense safety checks and log important notifications. 
    # Child functions should be careful to implement execTrade and set all object properties with
    # the API response 
    # 
    # Some of the methods are not fully utilized, or could most likely be
    # eliminated/refactored. (Example is `checkOrderComplete()`, which is called from `Action`, and
    # in turn from a Button (!!!).
    # 
    # 
    #===========================================================================
    
    
    def __init__(self, market, orderDetails, tradeAPI):
        #=======================================================================
        # On init, the order is validated and important properties set
        # 
        # :param market: (Market) - the market object that the order is for
        # :param orderDetails: (OrderDetails) - The object with all the order details
        # :param tradeAPI: (API) - Exchange API object (could be a fake API to use for testing)
        #=======================================================================
        self.market = market

        self._marketName     = orderDetails.marketName()
        self._quantity       = orderDetails.quantity()
        self._rate           = orderDetails.rate()
        self._orderType      = orderDetails.orderType()
        self._timeInEffect   = orderDetails.timeInEffect()
        self._conditionType  = orderDetails.conditionType()
        self._target         = orderDetails.target()
        self._validationType = orderDetails.validationType()

        self._api = tradeAPI
        if self._api.isLiveAPI():
            log.debug("LIVE TRADE")
        else:
            log.debug("FAKE TRADE")

        self.isValid = self.validate()

        if not self.isValid:
            Error("Could not initialize Order")
            log.info("Could not initialize order")

        self._isOrderComplete = False
        self.success = False
        self._orderID = None

        # Invalid trade rate... 
        self._tradeRate = -1.
        self._tradeQty = -42.




    def validate(self):
        #=======================================================================
        # Validates the order in three cases
        #
        # * FULL: Validation criteria (requires API call)
        #   - No open orders, buy or sell
        #   - No pending balances
        #
        # * STEANDARD: Validation criteria (API call not required)
        #   - No open sell orders
        #
        # * NONE: No validation performed
        # 
        # :returns: (Boolean) Whether order fits criteria listed above
        #=======================================================================
        _isValid = True

        # FULL vaidation - All open buy and sell orders for a given market
        if self._validationType == "FULL":
            orderInfo = self.getOpenOrderInfo()

            # Cannot retrieve order info
            if not orderInfo:
                log.info("ERROR: Cannot retrieve open order info for " + self._marketName)
                Error("Error -- Cannot retrieve open order info for " + self._marketName)
                return False
            # Pending buy/sell orders
            if self.orderInfo["buysTot"] or self.orderInfo["sellsTot"]:
                log.info("ALERT: Open order(s) in market " + self._marketName)
                Alert("Alert -- Open Order(s) in market " + self._marketName)
                _isValid = False
            # Deposit pending
            if self.market.pendingBalance() > 0:
                log.info("ALERT: Pending balance for market " + self._marketName)
                Alert("Alert -- Pending balance in market " + self._marketName)
                _isValid = False

        # STANDARD validation - No pending sell orders
        if self._validationType == "STANDARD":

            # Pending sell orders
            # if self.market.reservedBalance() > 0:
                # log.info("ALERT: Pending sell orders for market " + self._marketName)
                # Alert("Alert -- Pending balance in market " + self._marketName)
            if self.market.totalBalance() > 0:
                log.info("ALERT: Non-zero balance in market " + self._marketName)
                Alert("Alert -- Non-zero balance in market " + self._marketName)
                _isValid = False

        # Return validation status
        return _isValid

    def getOpenOrderInfo(self):
        #=======================================================================
        # Iterates through open orders and returns a dictionary with entries representing the summed
        # total amount of open buys, summed total amount of open sells, as well as the number of
        # open buys and the number of open sells 
        # 
        # :returns: (Dictionary/Boolean) a dictionary of information about open orders or False if
        # invalid 
        #=======================================================================
        response = self._api.get_open_orders(self._marketName)

        if (response["success"]):
            orderInfo = {}
            orderInfo["sells"] = 0
            orderInfo["buys"] = 0
            orderInfo["sellsTot"] = 0
            orderInfo["buysTot"] = 0
            for order in response["result"]:
                if (order["OrderType"] == "LIMIT_SELL"):
                    orderInfo["sells"] += 1
                    orderInfo["sellsTot"] += (float(order["Limit"])*float(order["Quantity"]))
                elif (order["OrderType"] == "LIMIT_BUY"):
                    orderInfo["buys"] += 1
                    orderInfo["buysTot"] += (float(order["Limit"])*float(order["Quantity"]))
                else:
                    log.info("Unknown order type - " + str(order))
            return orderInfo
        else:
            log.critical("ERROR: Could not fetch open orders - Order invalid")
            Error("Could Not fetch Open Orders--Order Invalid", self)
            return False

    # def checkOrderComplete(self):
    #     #=======================================================================
    #     # Checks whether the order has been completed.  Happens once per tick until true or destroyed
    #     # 
    #     # :returns: (Boolean) whether order has been completed
    #     #=======================================================================
    #     if self._orderID is not None:
    #         response = self._api.get_order(self._orderID)
    #         log.info(response)
    #        
    #         if response["success"]:
    #             if response["result"]["IsOpen"]:
    #                 self.completed = False
    #             else:
    #                 self.completed = True
    #                 self._isOrderComplete = True
    #                 log.info("SUCCESS: " + self._orderType + " " + self._buyOrSell +
    #                          " for market " + self._marketName + " executed successfully" + 
    #                          "\nOrder ID " + self._orderID)
    #                #  Alert("SUCCESS! Order for market " + self._orderID + " executed", self)  
    #                 return True
    #         else:
    #             log.critical("ERROR: Could not check order status for OrderID: " + str(self._orderID))
    #             # Error("Could Not Check Order Status: " + str(self._orderID), self)
    #     else:
    #         log.critical("ERROR: Could not find Order ID --- Status unknown")
    #         # Error("Could not find Order ID --- Status uknown", self)
    #      
    #     return False

    def cancel(self):
        #=======================================================================
        # Cancels order (not currently executed)
        # 
        # :returns: (Boolean) whether API call was successful
        # ..todo:: test this method
        #=======================================================================
        if self._orderID is not None:
            # Reset order completeness status
            self._isOrderComplete = False
            # Attempt order cancel
            response = self._api.cancel(self._orderID)
            if response["success"]:
                self._isOrderComplete = True
                return True
            else:
                Error("Error in Cancellation ---"+response["message"], self)

        else:
            Error("Could not find Order ID -- Cancel Failed", self)
        return False


    def logTradeResponse(self, bittrexTradeResponse):
        #=======================================================================
        # Logs the trade response after executing an order
        #=======================================================================
        # Succesful trade
        if bittrexTradeResponse["success"]:
            self._tradeRate = float(bittrexTradeResponse["result"]["Rate"])
            self._tradeQty  = float(bittrexTradeResponse["result"]["Quantity"])
            self._orderID   = bittrexTradeResponse["result"]["OrderId"]
            orderType = bittrexTradeResponse["result"]["OrderType"]

            grepInfo = self._marketName + " TRADE - "

            # Initialize log details defaults - BUY order
            logHeader       = orderType + " Order executed!!"
            logOrderID      = "Order ID: " + str(self._orderID)
            logBuySellCoins = "Bought: {:13.8f}".format(self._tradeQty) + " " + self.market.name
            logRatePaid     = "Effective rate: {:10.8f}".format(self._tradeRate)
            logMarketBidAsk = "Market ASK: {:10.8f}".format(self.market.ask())
            logTotalAmount  = "Total cost: {:10.8f}".format(self._tradeRate * self._tradeQty)
            
            # Overrides for SELL orders
            if bittrexTradeResponse["result"]["BuyOrSell"] == "Sell":
                logHeader       = orderType + " Order executed!!"
                logBuySellCoins = "Sold: {:13.8f}".format(self._tradeQty) + " " + self.market.name
                logMarketBidAsk = "Market BID: {:10.8f}".format(self.market.bid())
                logTotalAmount  = "Total proceeds: {:10.8f}".format(self._tradeRate*self._tradeQty)

            # Log to file
            log.info(grepInfo + str(bittrexTradeResponse) + "\n" +
                     grepInfo + logHeader       + "\n" +
                     grepInfo + logOrderID      + "\n" +
                     grepInfo + logBuySellCoins + "\n" +
                     grepInfo + logRatePaid     + "\n" +
                     grepInfo + logMarketBidAsk + "\n" +
                     grepInfo + logTotalAmount  + "\n")
            
            # Log to GUI
            Success(logHeader)
            Success(logBuySellCoins)
            Success(logRatePaid)
            Success(logMarketBidAsk)
            Success(logTotalAmount)

        # Something went wrong
        else:
            # Log to file
            log.critical("ERROR: Order failed with message: " + bittrexTradeResponse["message"])
            # log to GUI
            Error("Order failed: " + bittrexTradeResponse["message"])



    def marketName(self):
        #=======================================================================
        # :return: String - The market name for the order
        #=======================================================================
        return self._marketName

    def quantity(self):
        #=======================================================================
        # :returns: Double - The quantity of altcoins to trade
        #=======================================================================
        return self._quantity

    def rate(self):
        #=======================================================================
        # :returns: Double - The FX rate at which to place the order
        #=======================================================================
        return self._rate

    def orderType(self):
        #=======================================================================
        # :returns: String - The order type (MARKET, LIMIT, ...)
        #=======================================================================
        return self._orderType

    def timeInEffect(self):
        #=======================================================================
        # :returns: String - The "time in effect" for the order
        #=======================================================================
        return self._timeInEffect

    def conditionType(self):
        #=======================================================================
        # :returns: String - The "condition type" of the order
        #=======================================================================
        return self._conditionType

    def target(self):
        #=======================================================================
        # :returns: Double - The "target" parameter for the order
        # (Used in conjunction with "condition type")
        #=======================================================================
        return self._target

    def orderID(self):
        #=======================================================================
        # :returns: String - The order ID after a trade is exacuted
        #=======================================================================
        return self._orderID

    def tradeRate(self):
        #=======================================================================
        # :returns: Double - The effective trade rate
        # (Can be different from rate at which the order is placed for a market order)
        #=======================================================================
        return self._tradeRate

    def tradeQty(self):
        #=======================================================================
        # :returns: Double - The effective quantity of coins traded
        #=======================================================================
        return self._tradeQty

    def isOrderComplete(self):
        #=======================================================================
        # :returns: Bool - Is the order complete
        #=======================================================================
        return self._isOrderComplete










class BuyOrder(Order):
    #============================================
    # Child of Order that executes buys
    #============================================
    isBuy = True
    _buyOrSell = "BUY"

    def execTrade(self):
        # Reset order status
        self.success = False
        # Reset order complete status
        self._isOrderComplete = False

        if (self.isValid):
            # Place buy order
            response = self._api.trade_buy(market         = self._marketName,
                                           quantity       = self._quantity,
                                           rate           = self._rate,
                                           order_type     = self._orderType,
                                           time_in_effect = self._timeInEffect,
                                           condition_type = self._conditionType,
                                           target         = self._target)
            # Log response
            self.logTradeResponse(response)
            # Return
            if response.get("success", False):
                self._isOrderComplete = True
                self.success = True
                return response["result"]["OrderId"]
            else:
                self._isOrderComplete = True
                return False
        else:
            log.critical("Invalid order prevented from execution for market " + self._marketName)
            Error("Invalid Order Prevented from execution")
        return False

class SellOrder(Order):
    #============================================
    # Child of Order that executes sells
    #============================================
    isSell = True
    _buyOrSell = "SELL"

    def execTrade(self):
        # Reset order status
        self.success = False
        # Reset order complete status
        self._isOrderComplete = False

        if (self.isValid):
            # Place sell order
            response = self._api.trade_sell(market         = self._marketName,
                                            quantity       = self._quantity,
                                            rate           = self._rate,
                                            order_type     = self._orderType,
                                            time_in_effect = self._timeInEffect,
                                            condition_type = self._conditionType,
                                            target         = self._target)
            # Log response
            self.logTradeResponse(response)
            # Return
            if response.get("success", False):
                self._isOrderComplete = True
                self.success = True
                return response["result"]["OrderId"]
            else:
                self._isOrderComplete = True
                return False
        else:
            log.critical("Invalid order prevented from execution for market " + self._marketName)
            Error("Invalid Order Prevented from execution")
        return False

class LimitBuy(BuyOrder):
    #===========================================================================
    # Creates a Limit Buy order
    #===========================================================================
    def __init__(self, market, orderDetails, tradeAPI):
        super().__init__(market, orderDetails, tradeAPI)
        self._orderType = "LIMIT_BUY"

class MarketBuy(LimitBuy):
    #===========================================================================
    # Creates a Market Buy order for Bittrex:
    # - Time in Effect: IMMEDIATE_OR_CANCEL (no lingering limit orders)
    # - Rate is increased significantly to ensure the full order goes through
    # - Assumes the quantity to buy is estimated elsewhere
    #===========================================================================
    def __init__(self, market, orderDetails, tradeAPI):
        super().__init__(market, orderDetails, tradeAPI)
        self._timeInEffect = "IMMEDIATE_OR_CANCEL"
        self._rate = round(10.*self._rate, 8)

class LimitSell(SellOrder):
    #===========================================================================
    # Creates a Limit Sell
    #===========================================================================
    def __init__(self, market, orderDetails, tradeAPI):
        super().__init__(market, orderDetails, tradeAPI)
        self._orderType = "LIMIT_SELL"

class MarketSell(LimitSell):
    #===========================================================================
    # Creates a Market Sell order for Bittrex:
    # - Time in Effect: IMMEDIATE_OR_CANCEL (no lingering limit orders)
    # - Rate is decreased significantly to ensure the full order goes through
    # - Assumes the quantity to sell is estimated elsewhere
    #===========================================================================
    def __init__(self, market, orderDetails, tradeAPI):
        super().__init__(market, orderDetails, tradeAPI)
        self._timeInEffect = "IMMEDIATE_OR_CANCEL"
        self._rate = round(0.1*self._rate, 8)



# class MarketBuy(BuyOrder):
#     #===========================================================================
#     # Creates a Market Buy order
#     #===========================================================================
#     def __init__(self, market, orderDetails, tradeAPI):
#         super().__init__(market, orderDetails, tradeAPI)
#         self._orderType = "MARKET"
#         # Override rate to None for live trades
#         if self._api.isLiveAPI():
#             self._rate = None


# class MarketSell(SellOrder):
#     #===========================================================================
#     # Creates market Sell
#     #===========================================================================
#     def __init__(self, market, orderDetails, tradeAPI):
#         super().__init__(market, orderDetails, tradeAPI)
#         self._orderType = "MARKET"
#         # Override rate to None for live trades
#         if self._api.isLiveAPI():
#             self._rate = None


