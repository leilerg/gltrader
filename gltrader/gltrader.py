"""

This is the Entrypoint which generates the GUI

"""

import os
import kivy
import sys

import logging
log = logging.getLogger(__name__)

import threading
import yaml

from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.properties import ObjectProperty

from .trader import Trader
from .ui.screen_management import ScreenManagement
from .notification import Error, Alert

# import cProfile
from pprint import pprint as pp
from datetime import datetime


import socket
import builtins 

# import resource

kivy.require('1.10.0')
os.environ['GLTRADER_CONFIG'] = os.path.dirname(os.path.abspath(__file__))+'/../config.yaml'
os.environ['STRATEGIES_DIR'] = os.path.dirname(os.path.abspath(__file__))+'/strategies/'

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = sock.connect_ex(('127.0.0.1',80))


class GLTraderApp(App):

    #===========================================================================
    # 
    # Calls main app
    # 
    #===========================================================================


    #First thing first, read in the config file
    with open(os.environ['GLTRADER_CONFIG'] ) as config_file:
        #parse yaml
        config = yaml.load(config_file)

    #And instantiate trader object with the config 
    trader = Trader(config)

    tick = ObjectProperty()
    rootWidget = ObjectProperty()
    dataThread = None
    uiThread = None
    isTesting = False
    uilock = threading.Lock()
    printlock = threading.Lock()

    def get_application_config(self):
        #=======================================================================
        # Gets config file
        # :returns: (String) path to config file
        #=======================================================================
        return os.environ['KIVY_HOME']+'/config.ini'

    def build(self):
        #=======================================================================
        #Starts up Application.  Loads GUI from kv file, loads config file, gets markets, and starts tick
        # 
        #:returns: (kivy.Widget)
        #=======================================================================
        self.rootWidget = Builder.load_file('gltrader/ui/kv/gltrader.kv')
        self.last = None

        #If the config is messed up somehow, error        
        if not self.trader.config:
            log.info("Bad confirguation file")
            Error("badconfig")

        #Else, all is good with the config, wkae up the trader and schedule the alarm on periodic intervals
        else:
            self.wakeUpTrader()
            self.tick = Clock.schedule_interval(self.wakeUpTrader, self.trader.config["tick_period"])

        self.rootWidget.nScreen.info_layout.refresh()
        return self.rootWidget



    def wakeUpTrader(self, dt=None):
        #=======================================================================
        # Main function - Wakes up the trader to act.
        #
        # Also updates the GUI at each refresh
        #=======================================================================
        log.info("===================== Tick Start - Waking up trader... =====================")
        # Wake up the trader
        self.trader.wakeUp()
        # Refresh the GUI
        self.rootWidget.refresh()
        log.info("======================= Tick End - Widget refreshed ========================\n")
  
        




    def test(self):
        #=======================================================================
        # Runs 3 ticks of data update only for testing purposees
        #=======================================================================
        self.trader.refreshMarkets()
        Clock.schedule_once(self.trader.refreshMarkets, 5)
        Clock.schedule_once(self.trader.refreshMarkets, 5)
        Clock.schedule_once(self.trader.refreshMarkets, 5)

    def on_stop(self):
        #=======================================================================
        # Runs when kivy is quit normally
        #=======================================================================
        self.tick.cancel()

    def on_pause(self):
        #=======================================================================
        # Runs on sleep, or when clicking "pause" button
        #=======================================================================
        self.tick.cancel()

    def on_resume(self):
        #=======================================================================
        # Runs after waking up, or after clicking "resume" button
        #=======================================================================
        self.tick = Clock.schedule_interval(self.wakeUpTrader, self.trader.config["tick_period"])
