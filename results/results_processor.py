import numpy as np
import os
import pandas as pd

import plotly.graph_objects as go
import utilities as utilities

# TODO seperate out results processor for each module. 

class ResultsProcessor:
    """
    A class to process and visualize the results of portfolio backtests and simulations.

    Methods
    -------
    plot_portfolio_value(portfolio_value, output_filename, filename):
        Plots the portfolio value over time.
    
    plot_var_cvar(returns, portfolio_value, trading_frequency, output_filename, confidence_level, filename):
        Plots the portfolio returns with VaR and CVaR.
    """

    def __init__(self, output_filename):
        """
        Initializes the ResultsProcessor with a specified output filename.

        Parameters
        ----------
        output_filename : str
            The name of the file to save the output.
        """
        self.output_filename = output_filename

    def plot_all_scenarios(self, performance_data):
        """
        Plots the portfolio performance for all weighting strategies together.

        Parameters
        ----------
        performance_data : dict
            Dictionary where keys are strategy names and values are Series of portfolio values.
        """
        fig = go.Figure()

        for strategy, data in performance_data.items():
            fig.add_trace(go.Scatter(x=data.index, y=data, mode='lines', name=strategy))

        fig.update_layout(
            title='Portfolio Performance Across Different Weighting Strategies',
            xaxis_title='Date',
            yaxis_title='Portfolio Value ($)',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        utilities.save_html(fig, "all_weighting_scenarios.html", self.output_filename)
        fig.show()

    def plot_portfolio_value(self, portfolio_value, filename='portfolio_value.html'):
        """
        Plots the portfolio value over time and saves the plot as an HTML file.

        Parameters
        ----------
        portfolio_value : Series
            Series containing the portfolio values over time.
        filename : str
            The name of the file to save the plot. Default is 'portfolio_value.html'.
        """
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=portfolio_value.index, y=portfolio_value, mode='lines', name='Portfolio Value'))
        fig.update_layout(title='Portfolio Value Over Time', xaxis_title='Date', yaxis_title='Portfolio Value ($)')
        utilities.save_html(fig, filename, self.output_filename)

    def plot_var_cvar(self, returns, portfolio_value, trading_frequency, confidence_level=0.95, filename='var_cvar.html'):
        """
        Plots the portfolio returns with VaR and CVaR and saves the plot as an HTML file.

        Parameters
        ----------
        returns : Series
            Series containing the portfolio returns over time.
        portfolio_value : Series
            Series containing the portfolio values over time.
        trading_frequency : str
            The frequency of trades. Either 'monthly' or 'bi-monthly'.
        confidence_level : float, optional
            The confidence level for calculating VaR and CVaR. Default is 0.95.
        filename : str, optional
            The name of the HTML file to save the plot. Default is 'var_cvar.html'.
        """
        var, cvar = utilities.calculate_var_cvar(returns, confidence_level)
        cagr = utilities.calculate_cagr(portfolio_value, trading_frequency)
        avg_annual_return = utilities.calculate_average_annual_return(returns, trading_frequency)
        max_drawdown = utilities.calculate_max_drawdown(portfolio_value)

        fig = go.Figure()

        fig.add_trace(go.Histogram(x=returns.dropna(), nbinsx=30, name='Returns', opacity=0.75, marker_color='blue'))

        fig.add_shape(type="line",
                    x0=var, y0=0, x1=var, y1=1,
                    line=dict(color="Red", dash="dash"),
                    xref='x', yref='paper',
                    name=f'VaR ({confidence_level * 100}%): {var:.2%}')
        fig.add_shape(type="line",
                    x0=cvar, y0=0, x1=cvar, y1=1,
                    line=dict(color="Green", dash="dash"),
                    xref='x', yref='paper',
                    name=f'CVaR ({confidence_level * 100}%): {cvar:.2%}')

        fig.update_layout(
            title='Portfolio Returns with VaR and CVaR',
            xaxis_title='Returns',
            yaxis_title='Frequency',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="top",
                y=1.3,
                xanchor="center",
                x=0.5
            ),
            annotations=[
                dict(
                    xref='paper', yref='paper', x=0.5, y=1.25,
                    xanchor='center', yanchor='bottom',
                    text=f'CAGR: {cagr:.2%}',
                    showarrow=False
                ),
                dict(
                    xref='paper', yref='paper', x=0.5, y=1.2,
                    xanchor='center', yanchor='bottom',
                    text=f'Avg Annual Return: {avg_annual_return:.2%}',
                    showarrow=False
                ),
                dict(
                    xref='paper', yref='paper', x=0.5, y=1.15,
                    xanchor='center', yanchor='bottom',
                    text=f'Max Drawdown: {max_drawdown:.2%}',
                    showarrow=False
                ),
                dict(
                    xref='paper', yref='paper', x=0.5, y=1.1,
                    xanchor='center', yanchor='bottom',
                    text=f'VaR ({confidence_level * 100}%): {var:.2%}',
                    showarrow=False
                ),
                dict(
                    xref='paper', yref='paper', x=0.5, y=1.05,
                    xanchor='center', yanchor='bottom',
                    text=f'CVaR ({confidence_level * 100}%): {cvar:.2%}',
                    showarrow=False
                )
            ]
        )
        utilities.save_html(fig, filename, self.output_filename)

    def plot_monte_carlo_simulation(self, simulation_results, simulation_horizon, output_filename, filename='monte_carlo_simulation.html'):
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
            fig.update_layout(
                title='Monte Carlo Simulation of Portfolio Value',
                xaxis_title='Year',
                yaxis_title='Portfolio Value ($)',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            utilities.save_html(fig, filename, output_filename)

    def plot_monthly_returns_heatmap(self, returns, output_filename, filename='heatmap_of_monthly_returns.html'):
        # TODO add portfolio stats as a legend
        """
        Plots a heatmap of monthly returns with values shown as percentages on each cell.

        Parameters
        ----------
        returns : Series
            Series containing the monthly portfolio returns.
        """
        returns_df = returns.resample('M').sum().to_frame(name='Monthly Return')
        returns_df['Monthly Return'] *= 100 
        returns_df['Year'] = returns_df.index.year
        returns_df['Month'] = returns_df.index.month
        heatmap_data = returns_df.pivot('Year', 'Month', 'Monthly Return')
        heatmap_data = heatmap_data.reindex(columns=np.arange(1, 13))  

        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            y=heatmap_data.index,
            colorscale='Viridis',
            colorbar=dict(title="Return", tickformat=".2%")
        ))
        annotations = []
        for i in range(heatmap_data.shape[0]):
            for j in range(heatmap_data.shape[1]):
                value = heatmap_data.iloc[i, j]
                if not np.isnan(value):  
                    annotations.append(
                        dict(
                            text=f"{value:.2f}%",
                            x=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][j],
                            y=heatmap_data.index[i],
                            xref='x1',
                            yref='y1',
                            font=dict(color="black"),
                            showarrow=False
                        )
                    )
        fig.update_layout(
            title="Monthly Returns Heatmap",
            xaxis_title="Month",
            yaxis_title="Year",
            annotations=annotations
        )
        utilities.save_html(fig, filename, output_filename)

    def plot_yearly_returns_heatmap(self, returns, output_filename, filename='heatmap_of_yearly_returns.html'):
        # TODO add portfolio stats as a legend
        """
        Plots a heatmap of yearly returns with values shown as percentages on each cell.

        Parameters
        ----------
        returns : Series
            Series containing the portfolio returns.
        """
        returns_df = returns.resample('Y').sum().to_frame(name='Yearly Return')
        returns_df['Yearly Return'] *= 100  
        returns_df['Year'] = returns_df.index.year
        returns_df = returns_df.sort_values('Year')
        fig = go.Figure(data=go.Heatmap(
            z=[returns_df['Yearly Return'].values],  
            x=returns_df['Year'], 
            y=["Yearly Returns"],  
            colorscale='Viridis',
            colorbar=dict(title="Return", tickformat=".2%")
        ))
        annotations = []
        for i in range(returns_df.shape[0]):
            value = returns_df['Yearly Return'].iloc[i]
            annotations.append(
                dict(
                    text=f"{value:.2f}%",
                    x=returns_df['Year'].iloc[i],
                    y="Yearly Returns",
                    xref='x1',
                    yref='y1',
                    font=dict(color="black"),
                    showarrow=False
                )
            )
        fig.update_layout(
            title="Yearly Returns Heatmap",
            xaxis_title="Year",
            yaxis_title="",
            annotations=annotations
        )
        utilities.save_html(fig, filename, output_filename)
