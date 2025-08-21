import types
import pandas as pd
import pytest

# ---- Mocks ----
class _MockCG:
    def __init__(self, price_map=None, market_chart=None, search_resp=None):
        self._price_map = price_map or {}
        self._market_chart = market_chart or {
            "prices": [[1710000000000, 100.0], [1710000864000, 101.0]],
            "total_volumes": [[1710000000000, 2000.0], [1710000864000, 2500.0]],
            "market_caps": [[1710000000000, 1_000_000.0], [1710000864000, 1_050_000.0]],
        }
        self._search_resp = search_resp or {
            "coins": [{"id": "bitcoin", "symbol": "btc", "name": "Bitcoin"}]
        }

    def get_price(self, ids, vs_currencies):
        return {ids: {vs_currencies: self._price_map.get((ids, vs_currencies), 12345.67)}}

    def get_coin_market_chart_by_id(self, id, vs_currency, days, interval=None):
        return self._market_chart

    def search(self, query):
        return self._search_resp


class _MockExchange:
    def __init__(self, markets, ticker_price=123.45, ohlcv=None):
        self.markets = markets
        self._ticker_price = ticker_price
        self._ohlcv = ohlcv or [
            [1710000000000, 10, 12, 9, 11, 1000],
            [1710000864000, 11, 13, 10, 12, 2000],
        ]

    def load_markets(self):
        return self.markets

    def fetch_ticker(self, symbol):
        if symbol not in self.markets:
            raise Exception("Bad symbol")
        return {"last": self._ticker_price}

    def fetch_ohlcv(self, symbol, timeframe="1d", limit=30):
        if symbol not in self.markets:
            raise Exception("Bad symbol")
        return self._ohlcv


@pytest.fixture
def patch_modules(monkeypatch):
    # Patch CG across modules
    import cryptofinance.utils.get_price as gp
    import cryptofinance.utils.get_history as gh
    import cryptofinance.utils.search_symbol as ss
    import cryptofinance.utils.get_market_cap as gmc
    import cryptofinance.utils.get_volume as gv

    cg = _MockCG()
    monkeypatch.setattr(gp, "CoinGeckoAPI", lambda: cg, raising=True)
    monkeypatch.setattr(gh, "CoinGeckoAPI", lambda: cg, raising=True)
    monkeypatch.setattr(ss, "CoinGeckoAPI", lambda: cg, raising=True)
    monkeypatch.setattr(gmc, "CoinGeckoAPI", lambda: cg, raising=True)
    monkeypatch.setattr(gv, "CoinGeckoAPI", lambda: cg, raising=True)

    # Patch ccxt on get_price/get_history
    markets_binance = {"BTC/USDT": {}, "ETH/USDT": {}}
    markets_coinbase = {"BTC/USD": {}, "ETH/USD": {}}
    markets_kraken = {"XBT/USD": {}, "ETH/USD": {}}

    binance = _MockExchange(markets=markets_binance, ticker_price=54321.0)
    coinbase = _MockExchange(markets=markets_coinbase, ticker_price=54322.0)
    kraken = _MockExchange(markets=markets_kraken, ticker_price=54323.0)

    import cryptofinance.utils.get_price as gp2
    import cryptofinance.utils.get_history as gh2

    class _CCXTStub:
        @staticmethod
        def binance():
            return binance
        @staticmethod
        def coinbase():
            return coinbase
        @staticmethod
        def kraken():
            return kraken

    monkeypatch.setattr(
        gp2, "ccxt",
        types.SimpleNamespace(binance=_CCXTStub.binance, coinbase=_CCXTStub.coinbase, kraken=_CCXTStub.kraken),
        raising=True,
    )
    monkeypatch.setattr(
        gh2, "ccxt",
        types.SimpleNamespace(binance=_CCXTStub.binance, coinbase=_CCXTStub.coinbase, kraken=_CCXTStub.kraken),
        raising=True,
    )
    return cg, binance, coinbase, kraken

# ---- Tests ----

def test_get_price_coingecko_first(patch_modules):
    from cryptofinance import get_price
    px = get_price("btc_usd")
    assert isinstance(px, float)
    assert abs(px - 12345.67) < 1e-6

def test_get_price_fallback_binance(patch_modules):
    cg, binance, _, _ = patch_modules
    def fail_get_price(*args, **kwargs):
        raise Exception("CG down")
    cg.get_price = fail_get_price

    from cryptofinance import get_price
    px = get_price("btc_usd")
    assert abs(px - 54321.0) < 1e-6

def test_get_history_from_coingecko(patch_modules):
    from cryptofinance import get_history
    df = get_history("btc_usd", days=2, interval="daily")
    assert list(df.columns) == ["timestamp", "open", "high", "low", "close", "volume"]
    assert len(df) >= 2
    assert pd.api.types.is_datetime64_any_dtype(df["timestamp"])

def test_get_history_fallback_binance(patch_modules):
    cg, binance, _, _ = patch_modules
    def fail_chart(*args, **kwargs):
        raise Exception("CG down")
    cg.get_coin_market_chart_by_id = fail_chart

    from cryptofinance import get_history
    df = get_history("btc_usd", days=2, interval="daily")
    assert list(df.columns) == ["timestamp", "open", "high", "low", "close", "volume"]
    assert len(df) == 2

def test_search_symbol(patch_modules):
    from cryptofinance import search_symbol
    res = search_symbol("btc")
    assert isinstance(res, list)
    assert res and {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin"} in res

def test_get_market_cap(patch_modules):
    from cryptofinance import get_market_cap
    df = get_market_cap("btc_usd", days=2)
    assert list(df.columns) == ["timestamp", "market_cap"]
    assert len(df) >= 2

def test_get_volume(patch_modules):
    from cryptofinance import get_volume
    df = get_volume("btc_usd", days=2)
    assert list(df.columns) == ["timestamp", "volume"]
    assert len(df) >= 2

def test_plot_price_no_show(monkeypatch):
    import pandas as pd
    from cryptofinance.utils import plot_price as pp

    def fake_hist(symbol, days=30, interval="daily"):
        return pd.DataFrame({
            "timestamp": pd.to_datetime([1710000000000, 1710000864000], unit="ms"),
            "open": [10, 11],
            "high": [12, 13],
            "low": [9, 10],
            "close": [11, 12],
            "volume": [1000, 2000],
        })

    monkeypatch.setattr(pp, "get_history", fake_hist, raising=True)

    import plotly.graph_objects as go
    monkeypatch.setattr(go.Figure, "show", lambda self: None, raising=True)

    from cryptofinance import plot_price
    plot_price("btc_usd", days=2, interval="daily")
