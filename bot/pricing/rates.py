from decimal import Decimal
import requests
import time

class RateProvider:
    """Fetches BTC->XMR exchange rate"""
    
    def __init__(self):
        self.cache = None
        self.cache_time = 0
        self.cache_duration = 300  # 5 minutes
    
    def btc_to_xmr(self) -> Decimal:
        """Returns how many XMR per 1 BTC"""
        # Use cache if fresh
        if self.cache and (time.time() - self.cache_time) < self.cache_duration:
            return self.cache
        
        try:
            print("🔄 Fetching BTC->XMR rate from CoinGecko...")
            r = requests.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params={"ids": "monero", "vs_currencies": "btc"},
                timeout=10
            )
            r.raise_for_status()
            
            # Monero price in BTC (e.g., 0.00567)
            xmr_in_btc = Decimal(str(r.json()["monero"]["btc"]))
            
            # We want BTC per XMR, so invert
            btc_per_xmr = Decimal(1) / xmr_in_btc
            
            self.cache = btc_per_xmr
            self.cache_time = time.time()
            
            print(f"✅ Rate: 1 BTC = {btc_per_xmr:.4f} XMR")
            return btc_per_xmr
            
        except Exception as e:
            print(f"❌ Rate fetch failed: {e}")
            # Return a fallback rate
            return Decimal("157.0")  # Approximate fallback

if __name__ == "__main__":
    # Test it!
    provider = RateProvider()
    rate = provider.btc_to_xmr()
    print(f"\nTest: 0.5 BTC = {Decimal('0.5') * rate:.4f} XMR")