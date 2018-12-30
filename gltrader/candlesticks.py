
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
import statistics
import numpy

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
    previousDayCandles = []
    #List of the candles for the last hour
    lastHourCandles = []
    # Last/latest/most recent candle
    currentCandle = []
    #Previous day *hourly* volume average
    volumePrevDayHrAverage = 999999999
    #Last hour volume
    volumeLastHour = 999999999
    # Current/running volume (i.e. volume during the currently ongoing tick)
    currentVol = 999999999
    # Previous day average tick volume
    prevDayTickVolMean = 999999999
    # Previous day volume standard deviation
    prevDayTickVolStdev = 999999999
    # Previous day average tick base volume
    prevDayTickBsVolMean = 999999999
    # Previous day base volume standard deviation
    prevDayTickBsVolStdev = 999999999
    # Previous day high - 1 satoshi
    prevDayHigh = 0.00000001

    
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
        
        # Initialize all candles as dummy candles
        self.previousDayCandles = self.initDummyCandles(self.nrCandlesPerDay)
        self.lastHourCandles = self.initDummyCandles(self.nrCandlesPerHour)
        self.currentCandle = self.initDummyCandles(1)

        
        # Initialize with proper data - Sanity check the response is not empty
        # If allCandles contains enough data, and is not none
        if allCandles is not None and len(allCandles) >= self.nrCandlesPerDay + self.nrCandlesPerHour:
            # Initialize candles for previous day - EXCLUDING LAST HOUR
            self.previousDayCandles = allCandles[-self.nrCandlesPerDay-1:-1]
            # Initialize candles for last hour
            self.lastHourCandles = allCandles[-self.nrCandlesPerHour:]
            # Initialize current candle
            self.currentCandle = allCandles[-1]

        #Get average *hourly* volume over past day
        self.volumePrevDayHrAverage = self.GetAverageVolume(self.previousDayCandles, HOURS_PER_DAY)
        # Calculate time frame of last hour candles
        # (Will generally be less than one hour as the last candle is still updating...)
        # Note on the timestamp hour: `(timeNow.hour + 23) % 24`
        # This is to ensure that `timeNow.hour - 1` is always [0,23], which otherwise isn't
        # when `timeNow.hour = 0`
        timeNow = datetime.now()
        self.lastHrCandleLocalTimestamp = datetime(timeNow.year, timeNow.month, timeNow.day,
                                                   (timeNow.hour + 23) % 24,
                                                   tickInterval*(timeNow.minute // tickInterval),
                                                   0, 0) + timedelta(minutes=tickInterval)
        elapsedTime = (timeNow - self.lastHrCandleLocalTimestamp).seconds/SECONDS_PER_HOUR
        # Finally, update the hourly average using the actual elapsed time
        self.volumeLastHour = self.GetAverageVolume(self.lastHourCandles, elapsedTime)

        # Set the derived market data for the previous day
        self.setPreviousDayDerivedMktData()

        # Log some candles
        log.debug("Previous day candles: " + str(self.previousDayCandles) + "\n" +
                  "Last hour candles: " + str(self.lastHourCandles) + "\n" +
                  "Current candle: " + str(self.currentCandle))
        
        #Set initialization flag all good
        self.IsInitOK = True
            







    def currentVol(self):
        #=======================================================================
        # :returns: Double - The traded volume during the current tickInterval
        #=======================================================================
        return self.currentCandle["V"]

    def currentBaseVol(self):
        #=======================================================================
        # :returns: Double - The traded base volume during the current tickInterval
        #=======================================================================
        return self.currentCandle["BV"]
        
    def currentOpen(self):
        #=======================================================================
        # :returns: Double - The open price during the current tickInterval
        #=======================================================================
        return self.currentCandle["O"]

    def currentClose(self):
        #=======================================================================
        # :returns: None
        # Explanation: This is ill defined as the tick interval is still ongoing...
        #=======================================================================
        return None

    def currentHigh(self):
        #=======================================================================
        # :returns: Double - The high price during the current tickInterval
        #=======================================================================
        return self.currentCandle["H"]

    def currentLow(self):
        #=======================================================================
        # :returns: Double - The low price during the current tickInterval
        #=======================================================================
        return self.currentCandle["L"]

    
       
    def previousDayLastOpen(self):
        #=======================================================================
        # :returns: Double - The open price of the last tick interval during the previous day
        #=======================================================================
        return self.previousDayCandles[-1]["O"]

    def previousDayLastClose(self):
        #=======================================================================
        # :returns: Double - The close price of the last tick interval during the previous day
        #=======================================================================
        return self.previousDayCandles[-1]["C"]
            
    def previousDayLastHigh(self):
        #=======================================================================
        # :returns: Double - The high price of the last tick interval during the previous day
        #=======================================================================
        return self.previousDayCandles[-1]["H"]

    def previousDayLastLow(self):
        #=======================================================================
        # :returns: Double - The low price of the last tick interval during the previous day
        #=======================================================================
        return self.previousDayCandles[-1]["L"]



    def previousDayHigh(self):
        #=======================================================================
        # :returns: Double - The previous day High (EXCLUDES current tick interval)
        #=======================================================================
        return self.prevDayHigh

    def previousDayTickVolMean(self):
        #======================================================================
        # :returns: Double - The average tick (altcoin) volume traded over the past day 
        #======================================================================
        return self.prevDayTickVolMean

    def previousDayTickVolStdev(self):
        #======================================================================
        # :returns: Double - The stdev pf the tick (altcoin) volume traded over the past day 
        #======================================================================
        return self.prevDayTickVolStdev

    def previousDayTickBsVolMean(self):
        #======================================================================
        # :returns: Double - The average tick base (bitcoin) volume traded over the past day
        #======================================================================
        return self.prevDayTickBsVolMean

    def previousDayTickBsVolStdev(self):
        #======================================================================
        # :returns: Double - The stdev pf the tick (bitcoin) volume traded over the past day
        #======================================================================
        return self.prevDayTickBsVolStdev




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
    # - getAllLastHrOpens():            Time series of open prices for all candels during previous day
    # - getAllLastHrCloses():           Time series of close prices for all candels during previous day
    # - getAllLastHrLows():             Time series of low prices for all candels during previous day
    # - getAllLastHrHighs():            Time series of high prices for all candels during previous day
    # - getAllLastHrVolumes():          Time series of volumes for all candels during previous day
    # - getAllLastHrBaseVolumes():      Time series of open prices for all candels during previous day
    #
    #================================================================================================

    def getAllPreviousDayOpens(self):
        #=======================================================================
        # :returns: List - A list with all the open prices from all the previous day candles
        #=======================================================================
        if self.previousDayCandles is not None:
            return self.getListOfValuesFromListOfDict(self.previousDayCandles, "O")
        else:
            return [0]

    def getAllPreviousDayCloses(self):
        #=======================================================================
        # :returns: List - A list with all the close prices from all the previous day candles
        #=======================================================================
        if self.previousDayCandles is not None:
            return self.getListOfValuesFromListOfDict(self.previousDayCandles, "C")
        else:
            return [0]

    def getAllPreviousDayLows(self):
        #=======================================================================
        # :returns: List - A list with all the low prices from all the previous day candles
        #=======================================================================
        if self.previousDayCandles is not None:
            return self.getListOfValuesFromListOfDict(self.previousDayCandles, "L")
        else:
            return [0]

    def getAllPreviousDayHighs(self):
        #=======================================================================
        # :returns: List - A list with all the high prices from all the previous day candles
        #=======================================================================
        if self.previousDayCandles is not None:
            return self.getListOfValuesFromListOfDict(self.previousDayCandles, "H")
        else:
            return [0]

    def getAllPreviousDayVolumes(self):
        #=======================================================================
        # :returns: List - A list with all the volumes from all the previous day candles
        #=======================================================================
        if self.previousDayCandles is not None:
            return self.getListOfValuesFromListOfDict(self.previousDayCandles, "V")
        else:
            return [0]

    def getAllPreviousDayBaseVolumes(self):
        #=======================================================================
        # :returns: List - A list with all the base volumes from all the previous day candles
        #=======================================================================
        if self.previousDayCandles is not None:
            return self.getListOfValuesFromListOfDict(self.previousDayCandles, "BV")
        else:
            return [0]

    def getAllLastHrOpens(self):
        #=======================================================================
        # :returns: List - A list with all the open prices from all the last hour candles
        #=======================================================================
        if self.lastHourCandles is not None:
            return self.getListOfValuesFromListOfDict(self.lastHourCandles, "O")
        else:
            return [0]

    def getAllLastHrCloses(self):
        #=======================================================================
        # :returns: List - A list with all the close prices from all the last hour candles
        #=======================================================================
        if self.lastHourCandles is not None:
            return self.getListOfValuesFromListOfDict(self.lastHourCandles, "C")
        else:
            return [0]

    def getAllLastHrLows(self):
        #=======================================================================
        # :returns: List - A list with all the low prices from all the last hour candles
        #=======================================================================
        if self.lastHourCandles is not None:
            return self.getListOfValuesFromListOfDict(self.lastHourCandles, "L")
        else:
            return [0]

    def getAllLastHrHighs(self):
        #=======================================================================
        # :returns: List - A list with all the high prices from all the last hour candles
        #=======================================================================
        if self.lastHourCandles is not None:
            return self.getListOfValuesFromListOfDict(self.lastHourCandles, "H")
        else:
            return [0]

    def getAllLastHrVolumes(self):
        #=======================================================================
        # :returns: List - A list with all the volumes from all the last hour candles
        #=======================================================================
        if self.lastHourCandles is not None:
            return self.getListOfValuesFromListOfDict(self.lastHourCandles, "V")
        else:
            return [0]

    def getAllLastHourBaseVolume(self):
        #=======================================================================
        # :returns: List - A list with all the base volume from all the previous day candles
        #=======================================================================
        if self.lastHourCandles is not None:
            return self.getListOfValuesFromListOfDict(self.lastHourCandles, "BV")
        else:
            return [0]








    def getListOfValuesFromListOfDict(self, listOfDict, key):
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
            if self.currentCandle["T"] == lastCandle["T"]:
                #Update last candle only
                self.currentCandle = lastCandle
                self.lastHourCandles[-1] = lastCandle

            #All candles need updating
            else:
                #=========================================
                # print("\nUPDATE ALL CANDLES!!!")
                # print("Previous day candles - Before")
                # pp(self.previousDayCandles)
                #=========================================
                try:
                    #Update bulk of 24hr candles
                    self.previousDayCandles[0:self.nrCandlesPerDay-1] = self.previousDayCandles[1:self.nrCandlesPerDay]
                    #update last daily candle
                    self.previousDayCandles[-1] = self.currentCandle

                    #Update bulk of last hour candles
                    self.lastHourCandles[0:self.nrCandlesPerHour-1] = self.lastHourCandles[1:self.nrCandlesPerHour]
                    #update last hourly candle
                    self.lastHourCandles[-1] = lastCandle
                    # Update current candle
                    self.currentCandle = lastCandle

                    #update average *hourly* volume over past day
                    self.volumePrevDayHrAverage = self.GetAverageVolume(self.previousDayCandles,
                                                                        HOURS_PER_DAY)
                    # Reset all the derived market data for the previous day
                    self.setPreviousDayDerivedMktData()

                except Exception as error:
                    log.exception("Unhandled exception in 'candlesticks.updateCandles()'\n" +
                                  "Error: " + str(error))

            # Last step - Update hourly volume - See __init__ for logic in below calculation
            elapsedTime = (datetime.now() - self.lastHrCandleLocalTimestamp).seconds/SECONDS_PER_HOUR
            # Finally, update the hourly average using the actual elapsed time
            self.volumeLastHour = self.GetAverageVolume(self.lastHourCandles, elapsedTime)
            # # Log some times...
            # log.debug("Elapsed time, in hours: " + str(elapsedTime))








    #================================================================================================
    #
    # Collection of setter methods used to (re-)set various derived market quantities.
    # Examples of derived market quantities are the average tick volume over the last day, the tick
    # volume standard deviation and so on.
    # 
    # The following methods are available
    # - setPreviousDayDerivedMktData(): (Re)Set every derived market quantity
    # - setPreviousDayHigh():           (Re)Set the previous day High price
    # - setPreviousDayTickVolMean():    (Re)Set the previous day average tick volume
    # - setPreviousDayTickVolStdev():   (Re)Set the previous day tick volume standard deviation
    # - setPreviousDayTickBsVolMean():  (Re)Set the previous day average tick base volume
    # - setPreviousDayTickBsVolStdev(): (Re)Set the previous day tick base volume standard deviation
    #
    #================================================================================================

    def setPreviousDayDerivedMktData(self):
        #=======================================================================
        # Setter method that computs all previous day derived market data
        # (Does not include the current tick... intentionally!)
        # 
        # Currently computes:
        # - High
        # - Average volume over all candles (altcoin volume mean)
        # - Average base volume over all candles (BTC volume mean)
        # - Standard deviation of volume over all candles (altcoin volume stdev)
        # - Standard deviation of base volume over all candles (BTC volume stdev)
        # 
        # :return:    None
        #=======================================================================
        # Set previous day high
        self.setPreviousDayHigh()
        # Set previous day average tick volume
        prevDayVolData = self.getAllPreviousDayVolumes()
        self.setPreviousDayTickVolMean(prevDayVolData)
        # Set previous day tick volume standard deviation
        self.setPreviousDayTickVolStdev(prevDayVolData, self.prevDayTickVolMean)
        # Set previous day averagve tick base volume
        prevDayVolData = self.getAllPreviousDayBaseVolumes()
        self.setPreviousDayTickBsVolMean(prevDayVolData)
        # Set previous day tick base volume standard deviation
        self.setPreviousDayTickBsVolStdev(prevDayVolData, self.prevDayTickBsVolMean)
        
    def setPreviousDayHigh(self, prevDayHighData = None):
        #=======================================================================
        # Setter method to compute previous day high
        # (Does not include the current tick... intentionally!)
        #
        # Inputs:
        #     prevDayHighData - :list: with time series of previous day highs
        # 
        # :return:    None
        # :rtype:     double
        #=======================================================================
        # If called with no data, extract it
        if prevDayHighData is None:
            prevDayHighData = self.getAllPreviousDayHighs()
        # Set previous day high
        self.prevDayHigh = numpy.max(prevDayHighData)

    def setPreviousDayTickVolMean(self, prevDayVolData = None):
        #=======================================================================
        # Setter method to compute previous day volume average across all ticks (altcoin volume)
        # (Does not include the current tick... intentionally!)
        #
        # Inputs:
        #     prevDayVolData - :list: with time series of previous day (altcoin) volumes
        # 
        # :return:    None
        #=======================================================================
        # If called with no data, extract it
        if prevDayVolData is None:
            prevDayVolData = self.getAllPreviousDayVolumes()
        # Set previous day high
        self.prevDayTickVolMean = statistics.mean(prevDayVolData)

    def setPreviousDayTickVolStdev(self, prevDayVolData = None, prevDayTickVolMean = None):
        #=======================================================================
        # Setter method to compute previous day volume standard deviation across all ticks
        # (Does not include the current tick... intentionally!)
        #
        # Inputs:
        #     prevDayVolData - :list: with time series of previous day (altcoin) volumes
        # 
        # :return:    None
        #=======================================================================
        # If called with no data, extract it
        if prevDayVolData is None:
            prevDayVolData = self.getAllPreviousDayVolumes()
        # If called without the mean, compute it
        if prevDayTickVolMean is None:
            prevDayTickVolMean = statistics.mean(prevDayVolData)
        # Set previous day high
        self.prevDayTickVolStdev = statistics.stdev(prevDayVolData, prevDayTickVolMean)

    def setPreviousDayTickBsVolMean(self, prevDayBsVolData = None):
        #=======================================================================
        # Setter method to compute previous day base volume average across all ticks (bitcoin volume)
        # (Does not include the current tick... intentionally!)
        #
        # Inputs:
        #     prevDayBsVolData - :list: with time series of previous day (bitcoin) volumes
        # 
        # :return:    None
        #=======================================================================
        # If called with no data, extract it
        if prevDayBsVolData is None:
            prevDayBsVolData = self.getAllPreviousDayBaseVolumes()
        # Set previous day high
        self.prevDayTickBsVolMean = statistics.mean(prevDayBsVolData)

    def setPreviousDayTickBsVolStdev(self, prevDayBsVolData = None, prevDayTickBsVolMean = None):
        #=======================================================================
        # Setter method to compute previous day base volume standard deviation across all ticks
        # (bitcoin volume)
        # (Does not include the current tick... intentionally!)
        #
        # Inputs:
        #     prevDayVolData - :list: with time series of previous day (bitcoin) volumes
        # 
        # :return:    None
        #=======================================================================
        # If called with no data, extract it
        if prevDayBsVolData is None:
            prevDayBsVolData = self.getAllPreviousDayBaseVolumes()
        # If called without the mean, compute it
        if prevDayTickBsVolMean is None:
            prevDayTickBsVolMean = statistics.mean(prevDayBsVolData)
        # Set previous day high
        self.prevDayTickBsVolStdev = statistics.stdev(prevDayBsVolData, prevDayTickBsVolMean)

        



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
        
    
    
    
    
    
