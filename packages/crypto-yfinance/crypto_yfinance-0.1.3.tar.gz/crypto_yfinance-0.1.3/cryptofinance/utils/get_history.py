# cryptofinance/utils/get_history.py
from pycoingecko import CoinGeckoAPI
import ccxt
import pandas as pd
from .coingecko_resolver import resolve_cg_id

def get_history(symbol: str, days: int = 30, interval: str = 'daily') -> pd.DataFrame:
    base, quote = symbol.lower().split('_')
    try:
        cg = CoinGeckoAPI()
        cg_id = resolve_cg_id(base.upper())
        cg_interval = 'hourly' if interval == 'hourly' else 'daily'
        data = cg.get_coin_market_chart_by_id(id=cg_id, vs_currency=quote, days=days, interval=cg_interval)
        prices = data['prices']
        volumes = data['total_volumes']
        df = pd.DataFrame(prices, columns=['timestamp', 'price'])
        df['volume'] = [v[1] for v in volumes]
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['open'] = df['price']; df['high'] = df['price']; df['low'] = df['price']; df['close'] = df['price']
        return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
    except Exception:
        pass

    # CCXT fallback (Binance → USDT if USD)
    bU, qU = base.upper(), quote.upper()
    quote_ccxt = "USDT" if qU == "USD" else qU
    symbol_ccxt = f"{bU}/{quote_ccxt}"
    try:
        ex = ccxt.binance()
        tf = {'daily': '1d', 'hourly': '1h'}[interval]
        ohlcv = ex.fetch_ohlcv(symbol_ccxt, timeframe=tf, limit=days)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        raise ValueError(f"History fetch failed for {symbol}: {e}")