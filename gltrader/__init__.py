import os

os.environ['GLTRADER_CONFIG'] = os.path.dirname(os.path.abspath(__file__))+'/../config.yaml'
os.environ['STRATEGIES_DIR'] = os.path.dirname(os.path.abspath(__file__))+'/strategies/'
