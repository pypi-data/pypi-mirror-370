# cryptofinance

Created by [Aakash Chavan Ravindranath](https://www.linkedin.com/in/aakashcr/)  
More content: [Medium](https://medium.com/@craakash)

A Python library for unified access to cryptocurrency data, similar to `yfinance`.  
Designed for retail investors and data scientists.

## Features

- `get_price()` – real-time spot price
- `get_history()` – OHLCV historical data
- `search_symbol()` – resolve ticker names
- `get_market_cap()` – historical market cap
- `get_volume()` – historical trading volume
- `plot_price()` – quick chart of price history

## Install

Coming soon via PyPI.

## Usage

```python
from cryptofinance import get_price, get_history, plot_price

print(get_price('btc_usd'))
df = get_history('btc_usd')
plot_price('btc_usd')
```
