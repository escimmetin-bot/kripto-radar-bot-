"""
CryptoRadar | Canlı Çoklu Piyasa & Endeks Veri Motoru
BTC, ETH, SOL, XRP, DOGE, BNB anlık fiyatları ve Korku/Açgözlülük endeksi.
"""
import urllib.request
import json
from typing import Dict

COIN_SYMBOLS = {
    "BTC": "BTCUSDT",
    "ETH": "ETHUSDT",
    "SOL": "SOLUSDT",
    "XRP": "XRPUSDT",
    "DOGE": "DOGEUSDT",
    "BNB": "BNBUSDT"
}


def get_live_market_data() -> Dict:
    result = {
        "coins": {
            "BTC": {"price": "78,000", "change": 0.5, "symbol": "BTC"},
            "ETH": {"price": "2,450", "change": 1.2, "symbol": "ETH"},
            "SOL": {"price": "185", "change": 2.8, "symbol": "SOL"},
            "XRP": {"price": "0.58", "change": 0.4, "symbol": "XRP"},
            "DOGE": {"price": "0.15", "change": 3.1, "symbol": "DOGE"},
            "BNB": {"price": "590", "change": 0.8, "symbol": "BNB"}
        },
        "fng_value": "34",
        "fng_sentiment": "Korku"
    }

    # 1. Binance Tickers (Toplu / Çoklu)
    for coin, sym in COIN_SYMBOLS.items():
        try:
            req = urllib.request.Request(f"https://api.binance.com/api/v3/ticker/24hr?symbol={sym}", headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=4) as r:
                data = json.loads(r.read().decode("utf-8"))
                price = float(data.get("lastPrice", 0))
                change = float(data.get("priceChangePercent", 0))
                
                # Fiyat formatlama
                if price >= 100:
                    price_str = f"{price:,.0f}"
                elif price >= 1:
                    price_str = f"{price:,.2f}"
                else:
                    price_str = f"{price:.4f}"

                result["coins"][coin] = {
                    "price": price_str,
                    "change": round(change, 2),
                    "symbol": coin
                }
        except Exception:
            pass

    # Kolay erişim için ana BTC verileri
    btc_info = result["coins"].get("BTC", {})
    result["btc_price"] = btc_info.get("price", "78,000")
    result["btc_change"] = btc_info.get("change", 0.5)

    # 2. Alternative.me Fear & Greed Index
    try:
        req = urllib.request.Request("https://api.alternative.me/fng/?limit=1", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=4) as r:
            data = json.loads(r.read().decode("utf-8"))
            if data.get("data"):
                fng_item = data["data"][0]
                val = fng_item.get("value", "50")
                sent_en = fng_item.get("value_classification", "Neutral")
                tr_map = {
                    "Extreme Fear": "Aşırı Korku",
                    "Fear": "Korku",
                    "Neutral": "Nötr",
                    "Greed": "Açgözlülük",
                    "Extreme Greed": "Aşırı Açgözlülük"
                }
                result["fng_value"] = str(val)
                result["fng_sentiment"] = tr_map.get(sent_en, sent_en)
    except Exception:
        pass

    return result


def detect_relevant_coin(title: str, summary: str, market_data: dict) -> dict:
    """Haber metnine göre en ilgili coini seçer (Solana, Ethereum, XRP vb.)."""
    text = f"{title} {summary}".lower()
    coins = market_data.get("coins", {})

    if "solana" in text or " sol " in text:
        return coins.get("SOL", coins.get("BTC"))
    elif "ethereum" in text or " eth " in text or "vitalik" in text:
        return coins.get("ETH", coins.get("BTC"))
    elif "ripple" in text or "xrp" in text:
        return coins.get("XRP", coins.get("BTC"))
    elif "doge" in text or "dogecoin" in text:
        return coins.get("DOGE", coins.get("BTC"))
    elif "bnb" in text or "binance coin" in text:
        return coins.get("BNB", coins.get("BTC"))

    # Varsayılan lider coin: BTC
    return coins.get("BTC")


if __name__ == "__main__":
    d = get_live_market_data()
    print("Market:", {k: v for k, v in d.items() if k != "coins"})
    print("SOL:", d["coins"].get("SOL"))
    print("XRP:", d["coins"].get("XRP"))
