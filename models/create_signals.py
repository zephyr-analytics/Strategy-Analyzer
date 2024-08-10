import utilities
import plotly.graph_objects as go
from plotly.subplots import make_subplots  

class CreateSignals:
    def __init__(self, assets_weights, data, bond_ticker='SHV', cash_ticker='BIL', weighting_strategy='use_file_weights', sma_period=168):
        self.assets_weights = assets_weights
        self.data = data
        self.bond_ticker = bond_ticker
        self.cash_ticker = cash_ticker
        self.weighting_strategy = weighting_strategy
        self.sma_period = sma_period

    def generate_signals(self, current_date):
        latest_weights = utilities.adjusted_weights(
            self.assets_weights, self.data, self.bond_ticker, self.cash_ticker, 
            self.weighting_strategy, self.sma_period, current_date
        )
        self.plot_signals(latest_weights, current_date)

# TODO needs to be shifted to results processor
    def plot_signals(self, latest_weights, current_date):
            fig = make_subplots(
                rows=1, cols=2, 
                specs=[[{"type": "table"}, {"type": "domain"}]], 
                column_widths=[0.6, 0.4], 
                subplot_titles=("SMA Status", "Current Weights")
            )

            sma_status = []
            for ticker in self.assets_weights.keys():
                price = self.data.loc[:current_date, ticker].iloc[-1]
                sma = self.data.loc[:current_date, ticker].rolling(window=self.sma_period).mean().iloc[-1]
                status = "Above SMA" if price > sma else "Below SMA"
                sma_status.append(f"{ticker}: {status}")
            
            fig.add_trace(go.Table(
                header=dict(values=["Asset", "SMA Status"]),
                cells=dict(values=[list(self.assets_weights.keys()), sma_status]),
                columnwidth=[80, 200],  
            ), row=1, col=1)
            
            fig.add_trace(go.Pie(
                labels=list(latest_weights.keys()), 
                values=list(latest_weights.values()), 
                title="Current Portfolio Weights",
                textinfo='label+percent',  
                hoverinfo='label+value+percent',
                showlegend=True
            ), row=1, col=2)
            
            fig.update_layout(
                title_text=f"Portfolio Signals on {current_date}",
                height=600,  
                margin=dict(t=50, b=50, l=50, r=50)  
            )
            fig.show()
