"""
Processor for processing results from models.
"""

import plotly.express as px
import statsmodels.api as sm

import strategy_analyzer.utilities as utilities
from strategy_analyzer.models.models_data import ModelsData
from strategy_analyzer.results.models_results import ModelsResults


class ParameterTuningResultsProcessor:
    """
    A class to process and visualize the results of portfolio backtests and simulations.
    """
    def __init__(self, models_data: ModelsData, models_results: ModelsResults, results: dict):
        """
        Initializes the ResultsProcessor with the data from ModelsData.

        Parameters
        ----------
        data_models : ModelsData
            An instance of the ModelsData class containing all
            relevant parameters and data for processing results.
        """
        self.data_models = models_data
        self.results_models = models_results
        self.results = results

    def process(self):
        """
        """
        self.plot_parametertune_results(results=self.results)

    def plot_parametertune_results(self, results: dict, filename="parameter_tune"):
        """
        Plot results from strategy testing (Momentum or Moving Average).

        Parameters
        ----------
        results : dict
            Dictionary of results from parameter tuning.
        """
        if self.data_models.processing_type.startswith("MOMENTUM"):
            strategy_label = "Momentum_Strategy"
            strategy_format = [
                f"MA:{key[0]} Freq:{key[1]} Assets:{key[2]} Type:{key[3]}" for key in results.keys()
            ]
            title = f"Possible Momentum Strategies - {self.data_models.weights_filename}"
        elif self.data_models.processing_type.startswith("MA"):
            strategy_label = "Moving_Average_Strategy"
            strategy_format = [
                f"MA:{key[0]} Freq:{key[1]} Type:{key[2]}" for key in results.keys()
            ]
            title = f"Possible Moving Average Strategies - {self.data_models.weights_filename}"

        data = {
            strategy_label: strategy_format,
            "cagr": [round(v["cagr"] * 100, 2) for v in results.values()],
            "average_annual_return": [round(v["average_annual_return"] * 100, 2) for v in results.values()],
            "annual_volatility": [round(v["annual_volatility"] * 100, 2) for v in results.values()],
            "max_drawdown": [round(v["max_drawdown"] * 100, 2) for v in results.values()],
            "var": [round(v["var"] * 100, 2) for v in results.values()],
            "cvar": [round(v["cvar"] * 100, 2) for v in results.values()],
            "sharpe_ratio": [
                round(v["cagr"] / v["annual_volatility"], 2) if v["annual_volatility"] != 0 else None
                for v in results.values()
            ]
        }

        trimmed_twilight = px.colors.cyclical.Twilight[1:]
        fig = px.scatter(
            data,
            x='annual_volatility',
            y='cagr',
            color='sharpe_ratio',
            color_continuous_scale=trimmed_twilight[::-1],
            hover_data=[strategy_label, 'max_drawdown', 'var', 'cvar', "average_annual_return"],
            labels={
                "cagr": "Compound Annual Growth Rate",
                "annual_volatility": "Annual Volatility",
                "max_drawdown": "Maximum Drawdown",
                "cvar": "Conditional Value at Risk",
                "var": "Value at Risk",
                "sharpe_ratio": "Sharpe Ratio",
                "average_annual_return": "Annualized Return"
            },
            title=title,
            trendline="ols"
        )

        rf = 0.04
        market_return = max(data["cagr"]) / 100
        market_volatility = max(data["annual_volatility"]) / 100

        slope = (market_return - rf) / market_volatility

        cal_volatility = [0, market_volatility * 1.5]
        cal_return = [rf + slope * vol for vol in cal_volatility]

        fig.add_scatter(
            x=[v * 100 for v in cal_volatility],
            y=[r * 100 for r in cal_return],
            mode='lines',
            line=dict(color='red', width=2, dash='dash'),
            name='Capital Allocation Line'
        )

        # TODO add buy and hold as a marker to the plot.
        # for key, value in results.items():
        # if key == "Buy_and_Hold":
        #     fig.add_trace(
        #         go.Scatter(
        #             x=[round(value["annual_volatility"] * 100, 2)],
        #             y=[round(value["cagr"] * 100, 2)],
        #             mode='markers+text',
        #             marker=dict(size=15, color='red', symbol='asterisk'),
        #             text='* Buy & Hold',
        #             textposition='top center'
        #         )
        #     )

        chart_theme = "plotly_dark" if self.data_models.theme_mode.lower() == "dark" else "plotly"
        fig.update_layout(
            template=chart_theme,
            coloraxis_colorbar_title="Sharpe Ratio",
            annotations=[
                dict(
                    xref='paper', yref='paper', x=0.5, y=0.2,
                    text="© Zephyr Analytics",
                    showarrow=False,
                    font=dict(size=80, color="#f8f9f9"),
                    xanchor='center',
                    yanchor='bottom',
                    opacity=0.5
                )
            ]
        )

        utilities.save_html(
            fig,
            filename,
            self.data_models.weights_filename,
            self.data_models.processing_type
        )
