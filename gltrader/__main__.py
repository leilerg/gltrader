import os

# Configure the logger
import logging
os.environ['LOG_FILE'] = os.path.dirname(os.path.abspath(__file__)) + '/../gltrader.log'
logger = logging.getLogger("gltrader")

logger.setLevel(logging.DEBUG)

# Create handlers
# File handler
fh = logging.FileHandler(os.environ["LOG_FILE"])
fh.setLevel(logging.DEBUG)
# Console handler
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# Formatter, to be added to the file handler
formatter = logging.Formatter("%(levelname)s - %(asctime)s - %(name)s: %(message)s")
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# Add handler to logger
logger.addHandler(fh)
logger.addHandler(ch)


import sys
# os.environ['KIVY_HOME'] = os.path.dirname(os.path.abspath(__file__))+'/../kivy'


from gltrader.gltrader import GLTraderApp

if __name__ == '__main__':
    logger.info("Starting GLTrader...")
    GLTraderApp().run()
