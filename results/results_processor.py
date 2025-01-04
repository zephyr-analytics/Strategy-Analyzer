"""
Processor for processing results from models.
"""

import numpy as np
import pandas as pd
import plotly.subplots as sp
import plotly.graph_objects as go

import utilities as utilities
from models.models_data import ModelsData

class ResultsProcessor:
    """
    A class to process and visualize the results of portfolio backtests and simulations.
    """

    def __init__(self, data_models: ModelsData):
        """
        Initializes the ResultsProcessor with the data from ModelsData.

        Parameters
        ----------
        data_models : ModelsData
            An instance of the ModelsData class containing all
            relevant parameters and data for processing results.
        """
        self.data_models = data_models
        self.output_filename = data_models.weights_filename
        self.portfolio_values = data_models.portfolio_values
        self.trading_frequency = data_models.trading_frequency
        self.portfolio_returns = data_models.portfolio_returns
        self.cagr = data_models.cagr
        self.max_drawdown = data_models.max_drawdown
        self.var = data_models.var
        self.cvar = data_models.cvar
        self.avg_annual_return = data_models.average_annual_return
        self.standard_deviation = data_models.annual_volatility
        self.buy_and_hold_values = data_models.buy_and_hold_values
        self.weights_filename = data_models.weights_filename
        self.num_assets = data_models.num_assets_to_select
        self.processing_type = data_models.processing_type
        self.ma_window = data_models.ma_window
        self.theme = data_models.theme_mode
        self.ma_type = data_models.ma_type
        self.benchmark_values = data_models.benchmark_values


    def plot_portfolio_value(self, filename='portfolio_value'):
        """
        Plots the portfolio value over time, including optional buy-and-hold and benchmark strategy lines,
        and saves the plot as an HTML file.

        Parameters
        ----------
        filename : str, optional
            The name of the file to save the plot. Default is 'portfolio_value.html'.
        """
        portfolio_value = self.portfolio_values
        final_value = portfolio_value.iloc[-1]
        
        if self.theme.lower() == "dark":
            line_color = "white"
        else:
            line_color = "black" 

        fig = go.Figure()

        # Plot Portfolio Value
        fig.add_trace(go.Scatter(
            x=portfolio_value.index,
            y=portfolio_value,
            mode='lines',
            name='Portfolio Value',
            line=dict(color=line_color)
        ))

        # Plot Buy-and-Hold Values if available
        if self.buy_and_hold_values is not None:
            final_bnh_value = self.buy_and_hold_values.iloc[-1]
            fig.add_trace(go.Scatter(
                x=self.buy_and_hold_values.index,
                y=self.buy_and_hold_values,
                mode='lines',
                name='Buy & Hold Value',
                line=dict(color="#ce93d8")
            ))

        # Plot Benchmark Values if available
        if self.benchmark_values is not None and not self.benchmark_values.empty:
            final_benchmark_value = self.benchmark_values.iloc[-1]
            fig.add_trace(go.Scatter(
                x=self.benchmark_values.index,
                y=self.benchmark_values,
                mode='lines',
                name='Benchmark Value',
                line=dict(color="#ffa726")
            ))

        # Annotations
        annotations = [
            dict(
                xref='paper', yref='paper', x=0.2, y=1,
                xanchor='center', yanchor='bottom',
                text=f'Final Value: ${final_value:,.2f}',
                showarrow=False,
                font=dict(size=12)
            ),
            dict(
                xref='paper', yref='paper', x=0.4, y=1,
                xanchor='center', yanchor='bottom',
                text=f'CAGR: {self.cagr:.2%}',
                showarrow=False,
                font=dict(size=12)
            ),
            dict(
                xref='paper', yref='paper', x=0.6, y=1,
                xanchor='center', yanchor='bottom',
                text=f'Max Drawdown: {self.max_drawdown:.2%}',
                showarrow=False,
                font=dict(size=12)
            ),
            dict(
                xref='paper', yref='paper', x=0.8, y=1,
                xanchor='center', yanchor='bottom',
                text=f'Standard Deviation: {self.standard_deviation:.2%}',
                showarrow=False,
                font=dict(size=12)
            )
        ]

        if self.buy_and_hold_values is not None:
            annotations.append(
                dict(
                    xref='paper', yref='paper', x=0.25, y=0.95,
                    xanchor='center', yanchor='bottom',
                    text=f'Final Value (B&H): ${final_bnh_value:,.2f}',
                    showarrow=False,
                    font=dict(size=12)
                )
            )

        if self.benchmark_values is not None and not self.benchmark_values.empty:
            annotations.append(
                dict(
                    xref='paper', yref='paper', x=0.5, y=0.95,
                    xanchor='center', yanchor='bottom',
                    text=f'Final Value (Benchmark): ${final_benchmark_value:,.2f}',
                    showarrow=False,
                    font=dict(size=12)
                )
            )

        annotations.append(
            dict(
                xref='paper', yref='paper', x=0.5, y=0.2,
                text="© Zehpyr Analytics",
                showarrow=False,
                font=dict(size=80, color="#f8f9f9"),
                xanchor='center',
                yanchor='bottom',
                opacity=0.5
            )
        )

        chart_theme = "plotly_dark" if self.theme.lower() == "dark" else "plotly"

        fig.update_layout(
            template=chart_theme,
            title=dict(
                text=f'Portfolio Value: {self.output_filename}, Assets: {self.num_assets}, Trading Freq: {self.trading_frequency}',
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
            self.weights_filename,
            self.ma_type,
            self.processing_type,
            self.num_assets,
            self.ma_window,
            self.trading_frequency
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
        returns = self.portfolio_returns
        portfolio_value = self.portfolio_values

        if self.theme.lower() == "dark":
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
                    x0=self.var, y0=0, x1=self.var, y1=1,
                    line=dict(color=line_color, dash="dash"),
                    xref='x', yref='paper',
                    name=f'VaR ({confidence_level * 100}%): {self.var:.2%}')
        fig.add_shape(type="line",
                    x0=self.cvar, y0=0, x1=self.cvar, y1=1,
                    line=dict(color=line_color, dash="dash"),
                    xref='x', yref='paper',
                    name=f'CVaR ({confidence_level * 100}%): {self.cvar:.2%}')

        chart_theme = "plotly_dark" if self.theme.lower() == "dark" else "plotly"
        
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
                    text=f'CAGR: {self.cagr:.2%}',
                    showarrow=False
                ),
                dict(
                    xref='paper', yref='paper', x=0.25, y=1,
                    xanchor='center', yanchor='bottom',
                    text=f'Avg Annual Return: {self.avg_annual_return:.2%}',
                    showarrow=False
                ),
                dict(
                    xref='paper', yref='paper', x=0.1, y=1,
                    xanchor='center', yanchor='bottom',
                    text=f'Max Drawdown: {self.max_drawdown:.2%}',
                    showarrow=False
                ),
                dict(
                    xref='paper', yref='paper', x=0.75, y=1,
                    xanchor='center', yanchor='bottom',
                    text=f'VaR ({confidence_level * 100}%): {self.var:.2%}',
                    showarrow=False
                ),
                dict(
                    xref='paper', yref='paper', x=0.9, y=1,
                    xanchor='center', yanchor='bottom',
                    text=f'CVaR ({confidence_level * 100}%): {self.cvar:.2%}',
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
            self.weights_filename,
            self.ma_type,
            self.processing_type,
            self.num_assets,
            self.ma_window,
            self.trading_frequency
        )


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
        average_cagr = utilities.calculate_cagr_monte_carlo(pd.Series(average_simulation))
        lower_cagr = utilities.calculate_cagr_monte_carlo(pd.Series(lower_bound))
        upper_cagr = utilities.calculate_cagr_monte_carlo(pd.Series(upper_bound))
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

        chart_theme = "plotly_dark" if self.theme.lower() == "dark" else "plotly"
        
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
            self.weights_filename,
            self.ma_type,
            self.processing_type,
            self.num_assets,
            self.ma_window,
            self.trading_frequency
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
        monthly_returns = self.portfolio_returns.resample('M').sum()
        yearly_returns = self.portfolio_returns.resample('Y').sum()
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

        chart_theme = "plotly_dark" if self.theme.lower() == "dark" else "plotly"
        
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
            fig, filename,
            self.weights_filename,
            self.ma_type,
            self.processing_type,
            self.num_assets,
            self.ma_window,
            self.trading_frequency
        )
