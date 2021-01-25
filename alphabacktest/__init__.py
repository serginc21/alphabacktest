from .alphabacktest import Engine
import os

__author__ = """Sergi Novellas"""
__email__ = 'sernocr@gmail.com'
__version__ = '0.1.5'


class Backtest(Engine):
    def __init__(self,sym="",
            initial_time="first",
            final_time="last",
            dateformat="%Y-%m-%d",
            file_path="",
            ticker=None,
            indicators=True,
            slippage=0.0001,
            leverage=1,
            fees=0.00005,
            capital=20000,
            save_results=True,
            save_path=os.getcwd(),
            plot_results=True):

        super().__init__(sym=sym,
            initial_time=initial_time,
            final_time=final_time,
            dateformat=dateformat,
            file_path=file_path,
            ticker=ticker,
            indicators=indicators,
            slippage=slippage,
            leverage=leverage,
            fees=fees,
            capital=capital,
            save_results=save_results,
            save_path=save_path,
            plot_results=plot_results)
