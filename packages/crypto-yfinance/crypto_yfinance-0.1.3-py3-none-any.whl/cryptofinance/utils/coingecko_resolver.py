# cryptofinance/utils/coingecko_resolver.py
from pycoingecko import CoinGeckoAPI

# Fast map for common assets; extend over time
CG_ID_MAP = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "BNB": "binancecoin",
    "XRP": "ripple",
    "ADA": "cardano",
    "SOL": "solana",
    "DOGE": "dogecoin",
    "DOT": "polkadot",
    "AVAX": "avalanche-2",
    "MATIC": "matic-network",
    "TRX": "tron",
    "LINK": "chainlink",
    "LTC": "litecoin",
    "ETC": "ethereum-classic",
    "ATOM": "cosmos",
    "XLM": "stellar",
}

def resolve_cg_id(symbol_upper: str) -> str:
    if symbol_upper in CG_ID_MAP:
        return CG_ID_MAP[symbol_upper]
    try:
        cg = CoinGeckoAPI()
        res = cg.search(symbol_upper)
        for c in res.get("coins", []):
            if c.get("symbol", "").upper() == symbol_upper:
                return c.get("id")
    except Exception:
        pass
    return symbol_upper.lower()
