# cryptofinance/utils/get_market_cap.py
from pycoingecko import CoinGeckoAPI
import pandas as pd
from .coingecko_resolver import resolve_cg_id

def get_market_cap(symbol: str, days: int = 30) -> pd.DataFrame:
    base, quote = symbol.lower().split('_')
    cg = CoinGeckoAPI()
    try:
        cg_id = resolve_cg_id(base.upper())
        data = cg.get_coin_market_chart_by_id(id=cg_id, vs_currency=quote, days=days)
        caps = data['market_caps']
        df = pd.DataFrame(caps, columns=['timestamp', 'market_cap'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        raise ValueError(f"Market cap fetch failed for {symbol}: {e}")