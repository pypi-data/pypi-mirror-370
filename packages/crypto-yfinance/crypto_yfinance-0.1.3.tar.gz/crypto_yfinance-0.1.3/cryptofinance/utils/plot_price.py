
import plotly.graph_objects as go
from .get_history import get_history

def plot_price(symbol: str, days: int = 30, interval: str = 'daily') -> None:
    df = get_history(symbol, days=days, interval=interval)
    fig = go.Figure(data=[go.Candlestick(
        x=df['timestamp'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close']
    )])
    fig.update_layout(
        title=f'{symbol.upper()} Price - Last {days} Days',
        xaxis_title='Date',
        yaxis_title='Price',
        xaxis_rangeslider_visible=False
    )
    fig.show()
