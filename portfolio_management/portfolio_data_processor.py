

import pandas as pd

from portfolio_management.portfolio_data import PortfolioData

class PortfolioDataProcessor:
    def __init__(self, data_portfolio: PortfolioData):
        # TODO there needs to be a data path supplied based on the selected file by the user.
        self.data_portfolio = data_portfolio.portfolio_dataframe

    def read_data(file_path):
        pass

    # TODO this then gets parsed and placed within portfolio_data.
    # TODO create the portfolio_data getter and setter.
    # TODO After the portoflio_data object will get passed to the portoflio analyzer.
    # TODO The portfolio analyzer will offer weighting based on adjusting weights of the strategy for best outcome. 
    # TODO Outcomes will then be judged based on optimization of best return with either least CVaR or least MaxDrawdown.
