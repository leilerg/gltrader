
#===============================================================================
# from _ast import Is
# Implements a "Candlesticks" class. 
#===============================================================================

import logging
from threading import currentThread
log = logging.getLogger(__name__)

from datetime import datetime, timedelta

from pprint import pprint as pp
from builtins import int
from threading import currentThread
from distutils.log import debug


HOURS_PER_DAY = 24
MINUTES_PER_HOUR = 60
SECONDS_PER_MINUTE = 60
SECONDS_PER_HOUR = MINUTES_PER_HOUR*SECONDS_PER_MINUTE

class CandleSticks:
    #Number of candles per hour... 
    nrCandlesPerHour = 1
    #Number of candles in a day
    nrCandlesPerDay = nrCandlesPerHour * HOURS_PER_DAY
    #List of all the candles for the previous day - EXCLUDING THE LAST HOUR
    PreviousDayCandles = []
    #List of the candles for the last hour
    LastHourCandles = []
    #Previous day *hourly* volume average
    volumePrevDayHrAverage = 0
    #Last hour volume
    volumeLastHour = 0

    #Flag - Initialization OK?
    IsInitOK = False
    

    def __init__(self, allCandles, totalTimeFrame=24, tickInterval=30):
        #=======================================================================
        # Class initialization. Should depend on the specific exchange.
        # As is, it's set up for the Bittrex API.
        #  
        # Takes as input a 
        #     :dict: - allCandles - Data with all the candles information
        #     :integer: - totalTimeFrame - Timeframe for the candlestick (chart) cover, in hours (Default: 24h)
        #     :integer: - tickInterval - Time interval of a single tick, in minutes (Default: 30min)
        #     
        # 
        # This is used to initialize the object  
        #=======================================================================

        #Calculate then number of candles in the object
        self.totalTimeFrame = totalTimeFrame
        self.tickInterval = tickInterval
        self.nrCandlesPerHour = int(MINUTES_PER_HOUR/self.tickInterval)
        self.nrCandlesPerDay = self.nrCandlesPerHour * HOURS_PER_DAY
        
        
        # Initialize with proper data - Sanity check the response is not empty
        # If allCandles contains enough data, and is not none
        if allCandles is not None and len(allCandles) >= self.nrCandlesPerDay + self.nrCandlesPerHour:
            #Initialize candles for previous day - EXCLUDING LAST HOUR
            self.PreviousDayCandles = allCandles[-self.nrCandlesPerDay-self.nrCandlesPerHour:-self.nrCandlesPerHour]
            #Initialize candles for last hour
            self.LastHourCandles = allCandles[-self.nrCandlesPerHour:]
        
        # Else, initialize with default/dummy data (prevent crashing if response from exchange is not valid)
        else:
            self.PreviousDayCandles = self.initDummyCandles(self.nrCandlesPerDay)
            self.LastHourCandles = self.initDummyCandles(self.nrCandlesPerHour)

        # Log
        log.debug(str(self.PreviousDayCandles))
        log.debug(str(self.LastHourCandles))


        #Get average *hourly* volume over past day
        self.volumePrevDayHrAverage = self.GetAverageVolume(self.PreviousDayCandles, HOURS_PER_DAY)
        
        # Calculate time frame of last hour candles
        # (Will generally be less than one hour as the last candle is still updating...)
        timeNow = datetime.now()
        self.lastHrCandleLocalTimestamp = datetime(timeNow.year, timeNow.month, timeNow.day,
                                                   timeNow.hour - 1,
                                                   tickInterval*(timeNow.minute // tickInterval),
                                                   0, 0) + timedelta(minutes=tickInterval)
        elapsedTime = (timeNow - self.lastHrCandleLocalTimestamp).seconds/SECONDS_PER_HOUR
        
        # Finally, update the hourly average using the actual elapsed time
        self.volumeLastHour = self.GetAverageVolume(self.LastHourCandles, elapsedTime)

        #Set initialization flag all good
        self.IsInitOK = True
            




    def volumeLastHr(self):
        #======================================================================
        # :returns: Double - The average volume traded over the last hour (all the ticks in the last hour)
        #======================================================================
        return self.volumeLastHour
    
    def avgVolPerHourPreviousDay(self):
        #=======================================================================
        # :returns: Double - The average hourly volume over the past day
        #=======================================================================
        return self.volumePrevDayHrAverage

    def lastOpen(self):
        #=======================================================================
        # :returns: Double - The open price during the last tickInterval
        #=======================================================================
        return self.LastHourCandles[-1]["O"]

    def lastClose(self):
        #=======================================================================
        # :returns: Double - The close price during the last tickInterval
        # CAVEAT: This is ill defined as the tick interval is still ongoing...
        #=======================================================================
        return self.LastHourCandles[-1]["C"]

    def lastHigh(self):
        #=======================================================================
        # :returns: Double - The high price during the last tickInterval
        #=======================================================================
        return self.LastHourCandles[-1]["H"]

    def lastLow(self):
        #=======================================================================
        # :returns: Double - The low price during the last tickInterval
        #=======================================================================
        return self.LastHourCandles[-1]["L"]

    def previousDayLastOpen(self):
        #=======================================================================
        # :returns: Double - The open price of the last tick interval during the previous day
        #=======================================================================
        return self.PreviousDayCandles[-1]["O"]

    def previousDayLastClose(self):
        #=======================================================================
        # :returns: Double - The close price of the last tick interval during the previous day
        #=======================================================================
        try:
            return self.PreviousDayCandles[-1]["C"]
        except:
            log.debug("Thread ID: " + str(currentThread().ident) +
                      ", Exception - candlesticks.previousDayLastClose()")
            return 999999999
            
    def previousDayLastHigh(self):
        #=======================================================================
        # :returns: Double - The high price of the last tick interval during the previous day
        #=======================================================================
        return self.PreviousDayCandles[-1]["H"]

    def previousDayLastLow(self):
        #=======================================================================
        # :returns: Double - The low price of the last tick interval during the previous day
        #=======================================================================
        return self.PreviousDayCandles[-1]["L"]




    #================================================================================================
    #
    # Set of methods that return a list with a time series of the various market metrics for a past
    # period, e.g. previous day or past hour. (The list is ordered as first element is oldest, last
    # element is most recent.) These methods are meant to be used for data analysis as part of a
    # strategy, e.g. by detecting patterns in the last day.
    #
    # The following methods are provided:
    #
    # PREVIOUS DAY:
    # - getAllPreviousDayOpens():       Time series of open prices for all candels during previous day
    # - getAllPreviousDayCloses():      Time series of close prices for all candels during previous day
    # - getAllPreviousDayLows():        Time series of low prices for all candels during previous day
    # - getAllPreviousDayHighs():       Time series of high prices for all candels during previous day
    # - getAllPreviousDayVolumes():     Time series of volumes for all candels during previous day
    # - getAllPreviousDayBaseVolumes(): Time series of open prices for all candels during previous day
    #
    # LAST HOUR:
    # - getAllLastHrOpens():       Time series of open prices for all candels during previous day
    # - getAllLastHrCloses():      Time series of close prices for all candels during previous day
    # - getAllLastHrLows():        Time series of low prices for all candels during previous day
    # - getAllLastHrHighs():       Time series of high prices for all candels during previous day
    # - getAllLastHrVolumes():     Time series of volumes for all candels during previous day
    # - getAllLastHrBaseVolumes(): Time series of open prices for all candels during previous day
    #
    #================================================================================================

    def getAllPreviousDayOpens(self):
        #=======================================================================
        # :returns: List - A list with all the open prices from all the previous day candles
        #=======================================================================
        if self.PreviousDayCandles is not None:
            return self.getListOfValuesFromListOfDict(self.PreviousDayCandles, "O")
        else:
            return [0]

    def getAllPreviousDayCloses(self):
        #=======================================================================
        # :returns: List - A list with all the close prices from all the previous day candles
        #=======================================================================
        if self.PreviousDayCandles is not None:
            return self.getListOfValuesFromListOfDict(self.PreviousDayCandles, "C")
        else:
            return [0]

    def getAllPreviousDayLows(self):
        #=======================================================================
        # :returns: List - A list with all the low prices from all the previous day candles
        #=======================================================================
        if self.PreviousDayCandles is not None:
            return self.getListOfValuesFromListOfDict(self.PreviousDayCandles, "L")
        else:
            return [0]

    def getAllPreviousDayHighs(self):
        #=======================================================================
        # :returns: List - A list with all the high prices from all the previous day candles
        #=======================================================================
        if self.PreviousDayCandles is not None:
            return self.getListOfValuesFromListOfDict(self.PreviousDayCandles, "H")
        else:
            return [0]

    def getAllPreviousDayVolumes(self):
        #=======================================================================
        # :returns: List - A list with all the volumes from all the previous day candles
        #=======================================================================
        if self.PreviousDayCandles is not None:
            return self.getListOfValuesFromListOfDict(self.PreviousDayCandles, "V")
        else:
            return [0]

    def getAllPreviousDayBaseVolumes(self):
        #=======================================================================
        # :returns: List - A list with all the base volumes from all the previous day candles
        #=======================================================================
        if self.PreviousDayCandles is not None:
            return self.getListOfValuesFromListOfDict(self.PreviousDayCandles, "BV")
        else:
            return [0]

    def getAllLastHrOpens(self):
        #=======================================================================
        # :returns: List - A list with all the open prices from all the last hour candles
        #=======================================================================
        if self.LastHourCandles is not None:
            return self.getListOfValuesFromListOfDict(self.LastHourCandles, "O")
        else:
            return [0]

    def getAllLastHrCloses(self):
        #=======================================================================
        # :returns: List - A list with all the close prices from all the last hour candles
        #=======================================================================
        if self.LastHourCandles is not None:
            return self.getListOfValuesFromListOfDict(self.LastHourCandles, "C")
        else:
            return [0]

    def getAllLastHrLows(self):
        #=======================================================================
        # :returns: List - A list with all the low prices from all the last hour candles
        #=======================================================================
        if self.LastHourCandles is not None:
            return self.getListOfValuesFromListOfDict(self.LastHourCandles, "L")
        else:
            return [0]

    def getAllLastHrHighs(self):
        #=======================================================================
        # :returns: List - A list with all the high prices from all the last hour candles
        #=======================================================================
        if self.LastHourCandles is not None:
            return self.getListOfValuesFromListOfDict(self.LastHourCandles, "H")
        else:
            return [0]

    def getAllLastHrVolumes(self):
        #=======================================================================
        # :returns: List - A list with all the volumes from all the last hour candles
        #=======================================================================
        if self.LastHourCandles is not None:
            return self.getListOfValuesFromListOfDict(self.LastHourCandles, "V")
        else:
            return [0]

    def getAllLastHourBaseVolume(self):
        #=======================================================================
        # :returns: List - A list with all the base volume from all the previous day candles
        #=======================================================================
        if self.LastHourCandles is not None:
            return self.getListOfValuesFromListOfDict(self.LastHourCandles, "BV")
        else:
            return [0]








    def getListOfValuesFromListOfDict(self, listOfDict, key)
        #=======================================================================
        # This method will construct a list of values corresponding to a specific key from a list of
        # dictionaries. 
        #
        # Input is
        #     :list: - listOfDict - List of dictionaries from which to extract data
        #     :string: - key - The dictionary key of the desired data
        # 
        # :returns: List - The list of all the values contained in the dictionaries
        #
        # Example: l = [{'key1': 'apple',  'key2': 2},
        #               {'key1': 'banana', 'key2': 3},
        #               {'key1': 'cars',   'key2': 4}] 
        #
        # By calling getListOfValuesFromListOfDict(l, "key1") the output will be
        #
        # lst = ['apple', 'banana', 'cars']
        #
        # It assumes all the dictionaries have the required key, and that the list is well formed,
        # i.e. that the input is indeed a list of dictionaries
        #
        #=======================================================================
        return [d[key] for d in listOfDict]



    def updateCandles(self, lastCandle):
        #=======================================================================
        # Method to update the CandleSticks with the latest CandleSticks
        #
        # Note: When checking what to update, last candle only or all candles
        # it will commit a small sin - Not accounting for the possible action
        # in the last interval when all the candles need to be updated. Overall, the 
        # impact is expected to be small, especially if a periodic re-initialization
        # is performed  
        # 
        # Input is
        #     :dict: - lastCandle - Data with the last candle
        # 
        # Does not return anything, it just updates the candels 
        #=======================================================================
        #Only update if initialization was OK
        if self.IsInitOK and lastCandle is not None:

            #Check if everything needs updating or last candle only
            if self.LastHourCandles[-1]["T"] == lastCandle["T"]:
                #Update last candle only
                self.LastHourCandles[-1] = lastCandle

            #All candles need updating
            else:
                #=========================================
                # print("\nUPDATE ALL CANDLES!!!")
                # print("Previous day candles - Before")
                # pp(self.PreviousDayCandles)
                #=========================================
                try:
                    #Update bulk of 24hr candles
                    self.PreviousDayCandles[0:self.nrCandlesPerDay-1] = self.PreviousDayCandles[1:self.nrCandlesPerDay]
                    #update last daily candle
                    self.PreviousDayCandles[-1] = self.LastHourCandles[0]
                    #update average *hourly* volume over past day
                    self.volumePrevDayHrAverage = self.GetAverageVolume(self.PreviousDayCandles, HOURS_PER_DAY)
    
                    #print("\nPrevious day candles - After")
                    #pp(self.PreviousDayCandles)
    
                    #Update bulk of last hour candles
                    self.LastHourCandles[0:self.nrCandlesPerHour-1] = self.LastHourCandles[1:self.nrCandlesPerHour]
                    #update last hourly candle
                    self.LastHourCandles[-1] = lastCandle

                    # Update current hour
                    self.lastHrCandleLocalTimestamp += timedelta(minutes=self.tickInterval)

                except:
                    log.debug("Thread ID: " + str(currentThread().ident) + 
                              ", Exception - candlesticks.updateCandles() - Replace all candles" +
                              "\nData dump - PreviousDayCandles: " + str(self.PreviousDayCandles) + 
                              "\nData dump - LastHourCandles: " + str(self.LastHourCandles))

            # Last step - Update hourly volume - See __init__ for logic in below calculation
            elapsedTime = (datetime.now() - self.lastHrCandleLocalTimestamp).seconds/SECONDS_PER_HOUR
            log.debug("Elapsed time, in hours: " + str(elapsedTime))

            # Finally, update the hourly average using the actual elapsed time
            self.volumeLastHour = self.GetAverageVolume(self.LastHourCandles, elapsedTime)


    
    def GetAverageVolume(self, candles, timeframe):
        #=======================================================================
        # Function to calculate the average volume for a 'candles' dictionary
        # 
        # Inputs:
        #     candles - :dict: with data
        #     timeframe - :integer: number of hours
        #     
        # :return:    Average volume over 'timeframe'
        # :rtype:     double
        #=======================================================================
        if timeframe <= 0:
            log.debug("Error in candlesticks.GetAverageVolume(self, candles, timeframe): \n" + 
                      "'timeframe' = " + timeframe + ", must be bigger than 0")
            return -1
        elif candles is None:
            log.debug("Error in candlesticks.GetAverageVolume(self, candles, timeframe): \n" +
                      "'candles' object is `None`")
            return -1
        else:
            avgVolume = 0
            for candle in candles:
                avgVolume = avgVolume + candle["V"]
            avgVolume = avgVolume/timeframe
                
            return avgVolume
    

    def initDummyCandles(self, nrCandles):
        #=======================================================================
        # :returns: List - A list with 'nrCandles' dummy candles (dictionaries) 
        #=======================================================================
        dummyCandlesList = []
        for i in range(0, nrCandles):
            dummyCandlesList.append(self.dummyCandle())
        
        return dummyCandlesList

    def dummyCandle(self):
        #=======================================================================
        # :returns: Dictionary - A dummy candle, building block for initializing the object 
        #=======================================================================
        return {
            "O" : 999., 
            "H" : 999.,
            "L" : 999.,
            "C" : 999.,
            "V" : 999999999.,
            "T" : "2000-01-01T00:00:00",
            "BV" : 99999999.
            }
    
    def BitrexCandlesKeys(self):
        #=======================================================================
        # :returns: List - All the keys in a Bittrex candles object
        #=======================================================================
        # "O" - Open
        # "C" - Close
        # "L" - Low
        # "H" - High
        # "V" - Volume (in shitcoin units)
        # "T" - Timestamp
        # "BV" - BaseVolume (in bitcoin)
        return ["O", "H", "L", "C", "V", "T", "BV"]
        
    
    
    
    
    
