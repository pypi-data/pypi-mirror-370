# cryptofinance/utils/get_volume.py
from pycoingecko import CoinGeckoAPI
import pandas as pd
from .coingecko_resolver import resolve_cg_id

def get_volume(symbol: str, days: int = 30) -> pd.DataFrame:
    base, quote = symbol.lower().split('_')
    cg = CoinGeckoAPI()
    try:
        cg_id = resolve_cg_id(base.upper())
        data = cg.get_coin_market_chart_by_id(id=cg_id, vs_currency=quote, days=days)
        vols = data['total_volumes']
        df = pd.DataFrame(vols, columns=['timestamp', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        raise ValueError(f"Volume fetch failed for {symbol}: {e}")