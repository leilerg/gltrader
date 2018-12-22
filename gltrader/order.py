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
    isSane = False
    orderType = "LIMIT"
    effect = "GOOD_TIL_CANCELLED"
    orderID = False

    def __init__(self, market, amount=None, rate=None, quantity=None):
        #=======================================================================
        # On init, the order is validated and important properties set
        # 
        # :param market: (Market) - the market object that the order is for
        # :param amount: (Float) - the amount in BTC (base currency) that should be traded (approximate for Market Orders)
        # :param rate: (Float) - used in limit orders to set the price
        #=======================================================================
        self.trader = App.get_running_app().trader
        if self.trader.config["live_trades"]:
            self.api = self.trader.api
            log.debug("LIVE TRADE")
        else:
            self.api = self.trader.fapi
            log.debug("FAKE TRADE")
        self.market = market
        # self.marketAbbr = "BTC-"+market.currency["Currency"]
        self.rate = rate
        self.qty = quantity
        self.amount = None
        if(amount):
            self.amount = self.parseAmount(amount)
        if (self.amount or self.qty):
            if self.amount:

                self.qty = self.getQty()
            self.orderInfo = self.getOpenOrderInfo()
            self.isValid = self.validate()
        else:
            Error("Could not initialize Order")
        self.isCompleted = False
        self.success = False
        self.orderID = False
        self.failed = False

    def checkOrderComplete(self):
        #=======================================================================
        # Checks whether the order has been completed.  Happens once per tick until true or destroyed
        # 
        # :returns: (Boolean) whether order has been completed
        #=======================================================================
        if(self.orderID):
            response = self.api.get_order(self.orderID)

            self.trader.calls = self.trader.calls + 1
            if response["success"]:
                if response["result"]["IsOpen"]:
                    self.completed = False
                else:
                    self.completed = True
                    self.success = True
                    return True
            else:
                Error("Could Not Check Order Status: "+self.orderID, self)
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
        if(self.orderID):
            response = self.api.cancel(self.orderID)
            if response["success"]:
                self.completed = True
                return True
            else:
                Error("Error in Cancellation ---"+response["message"], self)

        else:
            Error("Could not find Order ID -- Cancel Failed", self)
        return False

    def getQty(self):
        #=======================================================================
        # Calculates amount of traded (not BTC--base currency) tokens
        # 
        # :returns: (Float) Quantity of traded tokens
        #=======================================================================
        return self.amount/float(self.rate)

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

        if (self.qty and isinstance(self.qty, float) ):
            if (self.orderInfo):
                if (not self.orderInfo["buysTot"] and not self.orderInfo["sellsTot"] ) :
                    if (float(self.market.pendingBalance()) <= 0):
                        return True
                    else:
                        Alert("Error -- Pending Order(s)")
                else:
                    Alert("Error -- Open Order(s)")
            else:
                Error("Error -- no Order info: "+self.qty)
        else:
            Error("Error -- order qty invalid: "+self.qty)
        return False

    def parseAmount(self, amt):
        #=======================================================================
        # Makes sure amount is within range allowed
        # 
        # :param amt: (Float) The amount passed into the object
        # :returns: (Float/Boolean) The validated amount or False if invalid
        #=======================================================================

        self.minTrade = self.market.config["min_trade_amount"]
        self.maxTrade = self.market.config["max_trade_amount"]
        self.maxTradeTot = self.market.config["max_trade_total"]

        if (self.market.name in self.market.config):
            if ("min_trade_amount" in self.market.config):
                self.minTrade = self.market.config["min_trade_amount"]
            if ("max_trade_amount" in self.market.config):
                self.maxTrade = self.market.config["max_trade_amount"]
            if ("max_trade_total" in self.market.config):
                self.maxTradeTot = self.market.config["max_trade_total"]

        if (amt <= self.maxTrade and amt >= self.minTrade):
            return amt
        else:
            Error("trade amount out of range", self.market)
            log.debug("Max Trade: " + str(self.maxTrade) + "\n" +
                      "Min Trade: " + str(self.minTrade))
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
        response = self.api.get_open_orders("BTC-"+self.market.name)

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




#===============================================================================
# class MarketBuy_TEST(Order):
#     #===========================================================================
#     # Child of Order that executes Market Buys
#     #===========================================================================
#     isBuy = True
#     
#     # Set rate at 100x the current ask - Guarantees the entire order will go through for small orders
#     self.rate = self.market.ask()
#     
#     
#     def execTrade(self):
#         if self.isValid:
#             # Place the order on the exchange
#             response = self.api.trade_buy(
#                 market=self.market.abbr,
#                 order_type=self.orderType,
#                 quantity=self.qty,
#                 rate=self.rate,
#                 time_in_effect=self.effect
#             )
#             if response["success"]:
#                 self.isActive = True
#                 self.rate = float(response["result"]["Rate"])
#                 self.qty = float(response["result"]["Quantity"])
#                 self.orderID = response["result"]["OrderId"]
#                 # Success("Order "+self.orderID+"Executed: "+str(self.qty)+"x("+str(self.rate)+") = "+str(self.amount))
#                 Success("Order Executed: "+str(self.qty) + self.market.name + "x(" +
# str(self.rate)+ ") = " + str(self.amount) ) 
#                 return response["result"]["OrderId"]
#             else:
#                 Error("Order Failed: "+response["message"])
#         else:
#             Error("Invalid Order Prevented from execution")
#         self.completed = True
#         self.failed = True
#         return False
#===============================================================================
            



class LimitBuy(Order):
    #============================================
    # Child of Order that executes Limit Buys
    #============================================
    isBuy = True

    def execTrade(self):
        if (self.isValid):

            response = self.api.trade_buy(
                market=self.market.abbr,
                order_type=self.orderType,
                quantity=self.qty,
                rate=self.rate,
                time_in_effect=self.effect
            )
            self.trader.calls = self.trader.calls + 1
            if response["success"]:
                self.isActive = True
                self.rate = float(response["result"]["Rate"])
                self.qty = float(response["result"]["Quantity"])
                self.orderID = response["result"]["OrderId"]
                # Success("Order "+self.orderID+"Executed: "+str(self.qty)+"x("+str(self.rate)+") = "+str(self.amount))
                # Success("Order Executed: " + str(self.qty) + self.market.name + "x(" +
                # str(self.rate)+ ") = " + str(self.amount) ) 
                Success("BUY Order Executed! ")
                Success("Bought: {:16.8f}".format(self.qty) + " " + self.market.name)
                # Success("Rate: {:10.8f}".format(self.rate)) 
                Success("Rate: {:10.8f} ".format(self.market.ask()))
                Success("Total amount: " + str(self.amount))
                return response["result"]["OrderId"]
            else:
                Error("Order Failed: "+response["message"])
        else:
            Error("Invalid Order Prevented from execution")
        self.completed = True
        self.failed = True
        return False



class LimitSell(Order):
    #============================================
    # Child of Order that executes Limit Sells
    #============================================

    isSell = True


    def execTrade(self):
        if (self.isValid):
            response = self.api.trade_sell(
                market=self.market.abbr,
                order_type=self.orderType,
                quantity=self.qty,
                rate=self.rate,
                time_in_effect=self.effect
            )
            self.trader.calls = self.trader.calls + 1
            log.debug("Response: " + str(response))
            if response["success"]:
                self.isActive = True
                self.rate = response["result"]["Rate"]
                self.qty = response["result"]["Quantity"]
                self.orderID = response["result"]["OrderId"]
                # Success("SELL Order executed! " + self.orderID)
                Success("SELL Order executed! ")
                Success("Sold: {:16.8f}".format(self.qty) + " " + self.market.name) 
                # Success("Rate: {:10.8f}".format(self.rate)) 
                Success("Rate: {:10.8f} ".format(self.market.bid()))
                Success("Total amount: " +str(self.amount))
                return response["result"]["OrderId"]
            else:
                Error("Order Failed: "+response["message"])
        else:
            Error("Invalid Order Prevented from execution")
        self.completed = True
        self.failed = True
        return False





class MarketOrder(Order):
    #===========================================================================
    # Changes order to Market order --- Should never be called alone
    #===========================================================================

    orderType = "MARKET"
    rate = None
    


class MarketBuy(MarketOrder, LimitBuy):
    #===========================================================================
    # Creates market Buy, estimating qty and rate from latest tick
    #===========================================================================

    def getQty(self):
        # return self.amount/float(self.market.marketData.summary["Ask"])
        return self.amount/float(self.market.ask())

class MarketSell(MarketOrder, LimitSell):
    #===========================================================================
    # Creates market Sell, estimating qty and rate from latest tick
    #===========================================================================

    def getQty(self):
        # return self.amount/float(self.market.marketData.summary["Bid"])
        return self.amount/float(self.market.bid())
