
from pycoingecko import CoinGeckoAPI

def search_symbol(query: str) -> list:
    cg = CoinGeckoAPI()
    try:
        results = cg.search(query)
        coins = results.get('coins', [])
        return [{'id': c['id'], 'symbol': c['symbol'], 'name': c['name']} for c in coins]
    except Exception as e:
        raise ValueError(f"Symbol search failed: {e}")
