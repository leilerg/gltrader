from kivy.app import App
from .notification import *

import logging
log = logging.getLogger(__name__)



class Order(object):
    #===========================================================================
    # ***THESE METHODS HAVE NOT YET BEEN TESTED ON THE REAL API***
    # 
    # Orders are the objects which interface with API trades.  
    # They implement the last-defense safety checks and log important notifications.  
    # Child functions should be careful to implement execTrade and set all object properties with the API response
    #===========================================================================
    
    
    # def __init__(self, market, amount=None, rate=None, quantity=None):
    def __init__(self, market, orderDetails, tradeAPI):
        #=======================================================================
        # On init, the order is validated and important properties set
        # 
        # :param market: (Market) - the market object that the order is for
        # :param orderDetails: (OrderDetails) - The object with all the order details
        # :param tradeAPI: (API) - Exchange API object (could be a fake API to use for testing)
        #=======================================================================
        self.market = market

        self._marketName    = orderDetails.marketName()
        self._quantity      = orderDetails.quantity()
        self._rate          = orderDetails.rate()
        self._orderType     = orderDetails.orderType()
        self._timeInEffect  = orderDetails.timeInEffect()
        self._conditionType = orderDetails.conditionType()
        self._target        = orderDetails.target()

        
        self.api = tradeAPI
        # log.debug("LIVE TRADE")
        # log.debug("FAKE TRADE")

        self.orderInfo = self.getOpenOrderInfo()
        self.isValid = self.validate()
        # self.isValid = True

        # Invalid trade rate... 
        self._tradeRate = -1.
        self._tradeQty = -42.
        
        if not self.isValid:
            Error("Could not initialize Order")
        self.isCompleted = False
        self.success = False
        self._orderID = False
        self.failed = False

    def checkOrderComplete(self):
        #=======================================================================
        # Checks whether the order has been completed.  Happens once per tick until true or destroyed
        # 
        # :returns: (Boolean) whether order has been completed
        #=======================================================================
        if(self._orderID):
            response = self.api.get_order(self._orderID)

            if response["success"]:
                if response["result"]["IsOpen"]:
                    self.completed = False
                else:
                    self.completed = True
                    self.success = True
                    return True
            else:
                Error("Could Not Check Order Status: " + self._orderID, self)
        else:
            Error("Could not find Order ID --- status uknown", self)
        return False

    def cancel(self):
        #=======================================================================
        # Cancels order (not currently executed)
        # 
        # :returns: (Boolean) whether API call was successful
        # ..todo:: test this method
        #=======================================================================
        if(self._orderID):
            response = self.api.cancel(self._orderID)
            if response["success"]:
                self.completed = True
                return True
            else:
                Error("Error in Cancellation ---"+response["message"], self)

        else:
            Error("Could not find Order ID -- Cancel Failed", self)
        return False

    def validate(self):
        #=======================================================================
        # Validates based on the following criteria:
        # - No open orders
        # - No pending balances
        # # - Total trade amounts (open buys + sells) + this trade amount are less than total trade
        # amount (not exact for market orders) 
        # # - That's it for now
        # :returns: (Boolean) Whether order fits criteria listed above
        #=======================================================================

        if (self._quantity and isinstance(self._quantity, float)):
            if (self.orderInfo):
                if (not self.orderInfo["buysTot"] and not self.orderInfo["sellsTot"] ) :
                    if (float(self.market.pendingBalance()) <= 0):
                        return True
                    else:
                        log.debug("ALERT - Pending orders")
                        Alert("Error -- Pending Order(s)")
                else:
                    log.debug("ALERT - Open orders")
                    Alert("Error -- Open Order(s)")
            else:
                log.debug("ERROR - No order info: " + str(self._quantity))
                Error("Error -- no Order info: " + str(self._quantity))
        else:
            log.debug("ERROR - Order quantity invalid: " + str(self._quantity))
            Error("Error -- order qty invalid: " + str(self._quantity))
        return False

    def getOpenOrderInfo(self):
        #=======================================================================
        # Iterates through open orders and returns a dictionary with entries representing the summed
        # total amount of open buys, summed total amount of open sells, as well as the number of
        # open buys and the number of open sells 
        # 
        # :returns: (Dictionary/Boolean) a dictionary of information about open orders or False if
        # invalid 
        #=======================================================================
        response = self.api.get_open_orders(self._marketName)

        if (response["success"]):
            orderInfo = {}
            orderInfo["sells"] = 0
            orderInfo["buys"] = 0
            orderInfo["sellsTot"] = 0
            orderInfo["buysTot"] = 0
            for order in response["result"]:
                if (order["OrderType"] == "LIMIT_SELL"):
                    orderInfo["sells"] = orderInfo["sells"] + 1
                    orderInfo["sellsTot"] = orderInfo["sellsTot"] + (float(order["Limit"])*float(order["Quantity"]))
                elif (order["OrderType"] == "LIMIT_BUY"):
                    orderInfo["buys"] = orderInfo["buys"] + 1
                    orderInfo["buysTot"] = orderInfo["buysTot"] + (float(order["Limit"])*float(order["Quantity"]))
                else:
                    log.info("Unknown order type - " + str(order))
            return orderInfo
        else:
            Error("Could Not fetch Open Orders--Order Invalid", self)
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

            # Initialize log details defaults - BUY order
            logHeader       = "BUY Order executed!!"
            logOrderID      = "Order ID: " + str(self._orderID)
            logBuySellCoins = "Bought: {:11.4}".format(self._tradeQty) + " " + self.market.name
            logRatePaid     = "Effective rate: {:10.8}".format(self._tradeRate)
            logMarketBidAsk = "Market ASK: {:10.8}".format(self.market.ask())
            logTotalAmount  = "Total cost: {:10.8}".format(self._tradeRate * self._tradeQty)
            
            # Overrides for SELL orders
            if bittrexTradeResponse["result"]["BuyOrSell"] == "Sell":
                logHeader       = "SELL Order executed!!"
                logBuySellCoins = "Sold: {:11.4}".format(self._tradeQty) + " " + self.market.name
                logMarketBidAsk = "Market BID: {:10.8}".format(self.market.bid())
                logTotalAmount  = "Total proceeds: {:10.8}".format(self._tradeRate*self._tradeQty)

            # Log to file
            log.info(logHeader       + "\n" +
                     logOrderID      + "\n" +
                     logBuySellCoins + "\n" +
                     logRatePaid     + "\n" +
                     logMarketBidAsk + "\n" +
                     logTotalAmount  + "\n")
            
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






class BuyOrder(Order):
    #============================================
    # Child of Order that executes buys
    #============================================
    isBuy = True

    def execTrade(self):
        if (self.isValid):

            response = self.api.trade_buy(market         = self._marketName,
                                          quantity       = self._quantity,
                                          rate           = self._rate,
                                          order_type     = self._orderType,
                                          time_in_effect = self._timeInEffect,
                                          condition_type = self._conditionType,
                                          target         = self._target)

            # Log response
            self.logTradeResponse(response)
            # Return
            return response["result"]["OrderId"]
                           

        else:
            log.critical("Invalid order prevented from execution")
            Error("Invalid Order Prevented from execution")
        self.completed = True
        self.failed = True
        return False


class SellOrder(Order):
    #============================================
    # Child of Order that executes buys
    #============================================
    isSell = True

    def execTrade(self):
        if (self.isValid):

            response = self.api.trade_sell(market         = self._marketName,
                                           quantity       = self._quantity,
                                           rate           = self._rate,
                                           order_type     = self._orderType,
                                           time_in_effect = self._timeInEffect,
                                           condition_type = self._conditionType,
                                           target         = self._target)
            # Log response
            self.logTradeResponse(response)
            # Return
            return response["result"]["OrderId"]

        else:
            log.critical("Invalid order prevented from execution")
            Error("Invalid Order Prevented from execution")
        self.completed = True
        self.failed = True
        return False


class LimitBuy(BuyOrder):
    #===========================================================================
    # Creates a Market Buy order
    #===========================================================================
    _orderType = "LIMIT"

class MarketBuy(BuyOrder):
    #===========================================================================
    # Creates a Market Buy order
    #===========================================================================
    _orderType = "MARKET"
    _rate = None

class LimitSell(SellOrder):
    #===========================================================================
    # Creates market Sell, estimating qty and rate from latest tick
    #===========================================================================
    _orderType = "LIMIT"

class MarketSell(SellOrder):
    #===========================================================================
    # Creates market Sell, estimating qty and rate from latest tick
    #===========================================================================
    _orderType = "MARKET"
    _rate = None









# class LimitBuy(Order):
#     #============================================
#     # Child of Order that executes Limit Buys
#     #============================================
#     isBuy = True
#     _orderType = "LIMIT"

#     def execTrade(self):
#         if (self.isValid):

#             response = self.api.trade_buy(market         = self._marketName,
#                                           quantity       = self._quantity,
#                                           rate           = self._rate,
#                                           order_type     = self._orderType,
#                                           time_in_effect = self._timeInEffect,
#                                           condition      = self._conditionType,
#                                           target         = self._target)

#             # Log response
#             self.logTradeResponse(response)
#             # Return
#             return response["result"]["Order ID"]
            

#             # if response["success"]:
#             #     self.isActive = True
#             #     self._tradeRate = float(response["result"]["Rate"])
#             #     self._tradeQty  = float(response["result"]["Quantity"])
#             #     self._orderID = response["result"]["OrderId"]
#             #     # log some details,
#             #     log.info("BUY Order executed!!\n" +
#             #              "Order ID: " + str(self._orderID) + "\n" +
#             #              "Bought: " + str(self._tradeQty) + " " + self.market.name + "\n" +
#             #              "Rate paid: {:10.8}".format(self._tradeRate) + "\n" +
#             #              "Total amount: " + str(self._tradeRate*self._tradeQty))
#             #     Success("BUY Order Executed! ")
#             #     Success("Bought: {:16.8f}".format(self._tradeQty) + " " + self.market.name)
#             #     Success("Rate: {:10.8f}".format(self._tradeRate)) 
#             #     Success("ASK: {:10.8f} ".format(self.market.ask()))
#             #     Success("Total amount: {:10.8f} ".format(self._tradeRate*self._tradeQty))
#             #     return response["result"]["OrderId"]
#             # else:
#             #     Error("Order Failed: "+response["message"])
#         else:
#             log.critical("Invalid order prevented from execution")
#             Error("Invalid Order Prevented from execution")
#         self.completed = True
#         self.failed = True
#         return False


# class LimitSell(Order):
#     #============================================
#     # Child of Order that executes Limit Sells
#     #============================================
#     isSell = True
#     _orderType = "LIMIT"

#     def execTrade(self):
#         if (self.isValid):
#             response = self.api.trade_sell(market         = self._marketName,
#                                            quantity       = self._quantity,
#                                            rate           = self._rate,
#                                            order_type     = self._orderType,
#                                            time_in_effect = self._timeInEffect,
#                                            condition      = self._conditionType,
#                                            target         = self._target)

#             # Log response
#             self.logTradeResponse(response)
#             # Return
#             return response["result"]["Order ID"]
            
#             # if response["success"]:
#             #     self.isActive = True
#             #     self._tradeRate = float(response["result"]["Rate"])
#             #     self._tradeQty  = float(response["result"]["Quantity"])
#             #     self._orderID = response["result"]["OrderId"]
#             #     # log some details,
#             #     log.info("SELL Order executed!!\n" +
#             #              "Order ID: " + str(self._orderID) + "\n" +
#             #              "Bought: " + str(self._tradeQty) + " " + self.market.name + "\n" +
#             #              "Rate paid: {:10.8}".format(self._tradeRate) + "\n" +
#             #              "Total amount: " + str(self._tradeRate*self._tradeQty))
#             #     Success("SELL Order Executed! ")
#             #     Success("Sold: {:16.8f}".format(self._tradeQty) + " " + self.market.name)
#             #     Success("Rate: {:10.8f}".format(self._tradeRate)) 
#             #     Success("BID: {:10.8f} ".format(self.market.bid()))
#             #     Success("Total amount: {:10.8f} ".format(self._tradeRate*self._tradeQty))
#             #     return response["result"]["OrderId"]
#             # else:
#             #     Error("Order Failed: "+response["message"])
#         else:
#             log.critical("Invalid order prevented from execution")
#             Error("Invalid Order Prevented from execution")
            
#         self.completed = True
#         self.failed = True
#         return False


# class MarketBuy(Order):
#     #============================================
#     # Child of Order that executes Limit Buys
#     #============================================
#     isBuy = True
#     _orderType = "MARKET"
#     _rate = None

#     def execTrade(self):
#         if (self.isValid):

#             response = self.api.trade_buy(market         = self._marketName,
#                                           quantity       = self._quantity,
#                                           rate           = self._rate,
#                                           order_type     = self._orderType,
#                                           time_in_effect = self._timeInEffect,
#                                           condition      = self._conditionType,
#                                           target         = self._target)

#             # Log response
#             self.logTradeResponse(response)
#             # Return
#             return response["result"]["Order ID"]

#         else:
#             log.critical("Invalid order prevented from execution")
#             Error("Invalid Order Prevented from execution")
#         self.completed = True
#         self.failed = True
#         return False


# class MarketSell(Order):
#     #============================================
#     # Child of Order that executes Limit Sells
#     #============================================
#     isSell = True
#     _orderType = "MARKET"
#     _rate = None

#     def execTrade(self):
#         if (self.isValid):
#             response = self.api.trade_sell(market         = self._marketName,
#                                            quantity       = self._quantity,
#                                            rate           = self._rate,
#                                            order_type     = self,_orderType,
#                                            time_in_effect = self._timeInEffect,
#                                            condition      = self._conditionType,
#                                            target         = self._target)

#             # Log response
#             self.logTradeResponse(response)
#             # Return
#             return response["result"]["Order ID"]

#         else:
#             log.critical("Invalid order prevented from execution")
#             Error("Invalid Order Prevented from execution")
            
#         self.completed = True
#         self.failed = True
#         return False



# class MarketOrder(Order):
#     #===========================================================================
#     # Changes order to Market order --- Should never be called alone
#     #===========================================================================
#     orderType = "MARKET"
#     rate = None

# class MarketBuy(MarketOrder, BuyOrder):
#     #===========================================================================
#     # Creates a Market Buy order
#     #===========================================================================

# class MarketSell(MarketOrder, SellOrder):
#     #===========================================================================
#     # Creates market Sell, estimating qty and rate from latest tick
#     #===========================================================================
    

