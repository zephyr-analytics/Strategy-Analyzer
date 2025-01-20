"""
Processor for processing results from models.
"""

import numpy as np
import pandas as pd
import plotly.subplots as sp
import plotly.graph_objects as go

import strategy_analyzer.utilities as utilities
from strategy_analyzer.models.models_data import ModelsData
from strategy_analyzer.results.models_results import ModelsResults


class SimulationResultsProcessor:
    """
    A class to process and visualize the results of portfolio backtests and simulations.
    """
    def __init__(self, models_data: ModelsData, models_results: ModelsResults):
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

    def process(self):
        """
        Method for processing results from models.
        """
        self.plot_monte_carlo_simulation()

    def plot_monte_carlo_simulation(
            self,
            simulation_results,
            simulation_horizon,
            output_filename,
            filename='monte_carlo_simulation'
        ):
        """
        Plots the results of the Monte Carlo simulation.

        Parameters
        ----------
        simulation_results : DataFrame
            DataFrame containing the simulated portfolio values.
        simulation_horizon : int
            Number of years to simulate.
        output_filename : str
            The name of the file to save the output.
        filename : str, optional
            The name of the HTML file to save the plot. Default is 'monte_carlo_simulation.html'.
        """
        average_simulation = simulation_results.mean(axis=1)
        lower_bound = np.percentile(simulation_results, 5, axis=1)
        upper_bound = np.percentile(simulation_results, 95, axis=1)
        average_cagr = utilities.calculate_cagr(pd.Series(average_simulation))
        lower_cagr = utilities.calculate_cagr(pd.Series(lower_bound))
        upper_cagr = utilities.calculate_cagr(pd.Series(upper_bound))
        average_end_value = pd.Series(average_simulation).iloc[-1]
        lower_end_value = pd.Series(lower_bound).iloc[-1]
        upper_end_value = pd.Series(upper_bound).iloc[-1]
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(range(simulation_horizon + 1)),
            y=average_simulation,
            mode='lines',
            name=f'Average Simulation (CAGR: {average_cagr:.2%}, End Value: ${average_end_value:,.2f})',
            line=dict(color='blue')
        ))
        fig.add_trace(go.Scatter(
            x=list(range(simulation_horizon + 1)),
            y=lower_bound,
            mode='lines',
            name=f'Lower Bound (5%) (CAGR: {lower_cagr:.2%}, End Value: ${lower_end_value:,.2f})',
            line=dict(color='red', dash='dash')
        ))
        fig.add_trace(go.Scatter(
            x=list(range(simulation_horizon + 1)),
            y=upper_bound,
            mode='lines',
            name=f'Upper Bound (95%) (CAGR: {upper_cagr:.2%}, End Value: ${upper_end_value:,.2f})',
            line=dict(color='green', dash='dash')
        ))

        chart_theme = "plotly_dark" if self.data_models.theme_mode.lower() == "dark" else "plotly"

        fig.update_layout(
            template=chart_theme,
            title='Monte Carlo Simulation of Portfolio Value',
            xaxis_title='Year',
            yaxis_title='Portfolio Value ($)',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
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
