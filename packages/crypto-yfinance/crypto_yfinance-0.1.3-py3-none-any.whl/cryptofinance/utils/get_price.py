# cryptofinance/utils/get_price.py
from pycoingecko import CoinGeckoAPI
import ccxt
from .coingecko_resolver import resolve_cg_id

def _ccxt_try(exchange, symbols):
    try:
        exchange.load_markets()
        for s in symbols:
            if s in exchange.markets:
                return exchange.fetch_ticker(s)['last']
    except Exception:
        pass
    return None

def get_price(symbol: str) -> float:
    base, quote = symbol.lower().split('_')
    bU, qU = base.upper(), quote.upper()

    # Coingecko first
    try:
        cg = CoinGeckoAPI()
        cg_id = resolve_cg_id(bU)
        data = cg.get_price(ids=cg_id, vs_currencies=quote)
        val = data.get(cg_id, {}).get(quote)
        if val is not None:
            return float(val)
    except Exception:
        pass

    # CCXT fallbacks
    binance_symbols = [f"{bU}/USDT"] if qU == "USD" else [f"{bU}/{qU}"]
    coinbase_symbols = [f"{bU}/{qU}"]
    kr_base = "XBT" if bU == "BTC" else bU
    kraken_symbols = [f"{kr_base}/{qU}"]

    for ex, syms in (ccxt.binance(), binance_symbols), (ccxt.coinbase(), coinbase_symbols), (ccxt.kraken(), kraken_symbols):
        px = _ccxt_try(ex, syms)
        if px is not None:
            return float(px)

    raise ValueError(f"Price fetch failed for {symbol}: no market across Coingecko/Binance/Coinbase/Kraken")