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


class BacktestResultsProcessor:
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
        # TODO this needs to be adjusted for new portfolio data and statistics.
        self.plot_portfolio_value()
        self.plot_returns_heatmaps()
        self.plot_var_cvar()


    def plot_portfolio_value(self, filename='portfolio_value'):
        """
        Plots the portfolio value over time, including optional buy-and-hold and benchmark strategy lines,
        and saves the plot as an HTML file.

        Parameters
        ----------
        filename : str, optional
            The name of the file to save the plot. Default is 'portfolio_value.html'.
        """
        strategy_value = self.results_models.portfolio_values_non_con
        final_value = strategy_value.iloc[-1]

        portfolio_value = self.results_models.portfolio_values
        portfolio_final_value = portfolio_value.iloc[-1]


        if self.data_models.theme_mode.lower() == "dark":
            line_color = "white"
        else:
            line_color = "black"

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=strategy_value.index,
            y=strategy_value,
            mode='lines',
            name='Strategy Value',
            line=dict(color=line_color)
        ))

        if self.results_models.buy_and_hold_values is not None:
            fig.add_trace(go.Scatter(
                x=self.results_models.buy_and_hold_values.index,
                y=self.results_models.buy_and_hold_values,
                mode='lines',
                name='Buy & Hold Value',
                line=dict(color="#ce93d8")
            ))

        if self.results_models.benchmark_values is not None:
            fig.add_trace(go.Scatter(
                x=self.results_models.benchmark_values.index,
                y=self.results_models.benchmark_values,
                mode='lines',
                name='Benchmark Value',
                line=dict(color="#9b4aa5")
            ))

        fig.add_trace(go.Scatter(
            x=self.results_models.portfolio_values.index,
            y=self.results_models.portfolio_values,
            mode='lines',
            name='Portfolio Value',
            line=dict(color="#9b4aa5")
        ))

        annotations = [
            dict(
                xref='paper', yref='paper', x=0.2, y=1,
                xanchor='center', yanchor='bottom',
                text=f'Strategy Final Value: ${final_value:,.2f}',
                showarrow=False,
                font=dict(size=12)
            ),
            dict(
                xref='paper', yref='paper', x=0.4, y=1,
                xanchor='center', yanchor='bottom',
                text=f'CAGR: {self.results_models.cagr:.2%}',
                showarrow=False,
                font=dict(size=12)
            ),
            dict(
                xref='paper', yref='paper', x=0.6, y=1,
                xanchor='center', yanchor='bottom',
                text=f'Max Drawdown: {self.results_models.max_drawdown:.2%}',
                showarrow=False,
                font=dict(size=12)
            ),
            dict(
                xref='paper', yref='paper', x=0.8, y=1,
                xanchor='center', yanchor='bottom',
                text=f'Annual Volaility: {self.results_models.annual_volatility:.2%}',
                showarrow=False,
                font=dict(size=12)
            ),
            dict(
                xref='paper', yref='paper', x=0.2, y=0.95,
                xanchor='center', yanchor='bottom',
                text=f'Portfolio Final Value: ${portfolio_final_value:,.2f}',
                showarrow=False,
                font=dict(size=12)
            )
            # TODO need to add actual portfolio statistics.
        ]

        annotations.append(
            dict(
                xref='paper', yref='paper', x=0.5, y=0.2,
                text="© Zephyr Analytics",
                showarrow=False,
                font=dict(size=80, color="#f8f9f9"),
                xanchor='center',
                yanchor='bottom',
                opacity=0.5
            )
        )

        chart_theme = "plotly_dark" if self.data_models.theme_mode.lower() == "dark" else "plotly"

        fig.update_layout(
            template=chart_theme,
            title=dict(
                text=f'Portfolio Value: {self.data_models.weights_filename}',
                x=0.5,
                y=1,
                xanchor='center',
                yanchor='top'
            ),
            xaxis_title='Date',
            yaxis_title='Portfolio Value ($)',
            annotations=annotations,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=0.1,
                xanchor="center",
                x=0.5
            )
        )

        utilities.save_html(
            fig,
            filename,
            self.data_models.weights_filename,
            self.data_models.processing_type
        )


    def plot_var_cvar(self, confidence_level=0.95, filename='var_cvar'):
        """
        Plots the portfolio returns with VaR and CVaR and saves the plot as an HTML file.

        Parameters
        ----------
        confidence_level : float, optional
            The confidence level for calculating VaR and CVaR. Default is 0.95.
        filename : str, optional
            The name of the HTML file to save the plot. Default is 'var_cvar.html'.
        """
        # TODO this needs to use unadjusted returns.
        returns = self.results_models.portfolio_returns

        if self.data_models.theme_mode.lower() == "dark":
            line_color = "white"
        else:
            line_color = "black"

        fig = go.Figure()
        fig.add_trace(
            go.Histogram(
                x=returns.dropna(),
                nbinsx=30,
                name='Returns',
                opacity=0.75,
                marker_color="#ce93d8"
            )
        )
        fig.add_shape(type="line",
                    x0=self.results_models.var, y0=0, x1=self.results_models.var, y1=1,
                    line=dict(color=line_color, dash="dash"),
                    xref='x', yref='paper',
                    name=f'VaR ({confidence_level * 100}%): {self.results_models.var:.2%}')
        fig.add_shape(type="line",
                    x0=self.results_models.cvar, y0=0, x1=self.results_models.cvar, y1=1,
                    line=dict(color=line_color, dash="dash"),
                    xref='x', yref='paper',
                    name=f'CVaR ({confidence_level * 100}%): {self.results_models.cvar:.2%}')

        chart_theme = "plotly_dark" if self.data_models.theme_mode.lower() == "dark" else "plotly"

        fig.update_layout(
            template=chart_theme,
            title='Portfolio Returns with VaR and CVaR',
            xaxis_title='Returns',
            yaxis_title='Frequency',
            showlegend=False,
            legend=dict(
                orientation="h",
                yanchor="top",
                y=1.2,
                xanchor="center",
                x=0.5
            ),
            annotations=[
                dict(
                    xref='paper', yref='paper', x=0.5, y=1,
                    xanchor='center', yanchor='bottom',
                    text=f'CAGR: {self.results_models.cagr:.2%}',
                    showarrow=False
                ),
                dict(
                    xref='paper', yref='paper', x=0.25, y=1,
                    xanchor='center', yanchor='bottom',
                    text=f'Avg Annual Return: {self.results_models.average_annual_return:.2%}',
                    showarrow=False
                ),
                dict(
                    xref='paper', yref='paper', x=0.1, y=1,
                    xanchor='center', yanchor='bottom',
                    text=f'Max Drawdown: {self.results_models.max_drawdown:.2%}',
                    showarrow=False
                ),
                dict(
                    xref='paper', yref='paper', x=0.75, y=1,
                    xanchor='center', yanchor='bottom',
                    text=f'VaR ({confidence_level * 100}%): {self.results_models.var:.2%}',
                    showarrow=False
                ),
                dict(
                    xref='paper', yref='paper', x=0.9, y=1,
                    xanchor='center', yanchor='bottom',
                    text=f'CVaR ({confidence_level * 100}%): {self.results_models.cvar:.2%}',
                    showarrow=False
                ),
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


    def plot_returns_heatmaps(self, filename='returns_heatmap'):
        """
        Plots a combined heatmap of monthly and yearly
        returns with values shown as percentages on each cell.

        Parameters
        ----------
        filename : str, optional
            The name of the file to save the plot. Default is 'returns_heatmap.html'.
        """
        # TODO this needs to use unadjusted returns.
        monthly_returns = self.results_models.portfolio_returns.resample('M').sum()
        yearly_returns = self.results_models.portfolio_returns.resample('Y').sum()
        monthly_returns.index = monthly_returns.index + pd.DateOffset(months=1)
        monthly_returns_df = monthly_returns.to_frame(name='Monthly Return')
        monthly_returns_df['Monthly Return'] *= 100
        monthly_returns_df['Year'] = monthly_returns_df.index.year
        monthly_returns_df['Month'] = monthly_returns_df.index.month
        monthly_heatmap_data = monthly_returns_df.pivot('Year', 'Month', 'Monthly Return')
        monthly_heatmap_data = monthly_heatmap_data.reindex(columns=np.arange(1, 13))
        yearly_returns_df = yearly_returns.to_frame(name='Yearly Return')
        yearly_returns_df['Yearly Return'] *= 100
        yearly_returns_df['Year'] = yearly_returns_df.index.year
        yearly_returns_df = yearly_returns_df.sort_values('Year')

        all_returns = np.concatenate([
            monthly_heatmap_data.values.flatten(),
            yearly_returns_df['Yearly Return'].values
        ])
        zmin, zmax = np.nanmin(all_returns), np.nanmax(all_returns)

        fig = sp.make_subplots(
            rows=2, cols=1,
            subplot_titles=("Monthly Returns Heatmap", "Yearly Returns Heatmap"),
            shared_xaxes=False,
            row_heights=[0.75, 0.25],
            vertical_spacing=0.1
        )

        fig.add_trace(go.Heatmap(
            z=monthly_heatmap_data.values,
            x=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            y=monthly_heatmap_data.index,
            colorscale=[
                [0.0, 'red'],
                [(0 - zmin) / (zmax - zmin), 'white'],
                [1.0, 'green']
            ],
            zmin=zmin,
            zmax=zmax,
            showscale=False,
        ), row=1, col=1)
        monthly_annotations = []
        for i in range(monthly_heatmap_data.shape[0]):
            for j in range(monthly_heatmap_data.shape[1]):
                value = monthly_heatmap_data.iloc[i, j]
                if not np.isnan(value):
                    monthly_annotations.append(
                        dict(
                            text=f"{value:.2f}%",
                            x=[
                                'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
                            ][j],
                            y=monthly_heatmap_data.index[i],
                            xref='x1',
                            yref='y1',
                            font=dict(color="black"),
                            showarrow=False
                        )
                    )
        fig.add_trace(go.Heatmap(
            z=[yearly_returns_df['Yearly Return'].values],
            x=yearly_returns_df['Year'],
            y=["Yearly Returns"],
            colorscale=[
                [0.0, 'red'],
                [(0 - zmin) / (zmax - zmin), 'white'],
                [1.0, 'green']
            ],
            zmin=zmin,
            zmax=zmax,
            showscale=False,
        ), row=2, col=1)
        yearly_annotations = []
        for i in range(yearly_returns_df.shape[0]):
            value = yearly_returns_df['Yearly Return'].iloc[i]
            yearly_annotations.append(
                dict(
                    text=f"{value:.2f}%",
                    x=yearly_returns_df['Year'].iloc[i],
                    y="Yearly Returns",
                    xref='x2',
                    yref='y2',
                    font=dict(color="black"),
                    showarrow=False
                )
            )

        chart_theme = "plotly_dark" if self.data_models.theme_mode.lower() == "dark" else "plotly"

        fig.update_layout(
            template=chart_theme,
            annotations=monthly_annotations + yearly_annotations + [
                dict(
                    xref='paper', yref='paper', x=0.5, y=0.5,
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
