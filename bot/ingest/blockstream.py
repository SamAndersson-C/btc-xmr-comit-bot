import requests
import time
from typing import Optional

class BlockstreamAPI:
    """Fetches Bitcoin transaction data from Blockstream API"""
    
    def __init__(self):
        self.base_url = "https://blockstream.info/api"
        self.seen_txids = set()
    
    def get_recent_txids(self, limit: int = 50) -> list:
        """Get recent mempool transaction IDs"""
        try:
            r = requests.get(f"{self.base_url}/mempool/recent", timeout=10)
            r.raise_for_status()
            
            # Returns list of tx objects, extract txids
            txs = r.json()
            txids = [tx['txid'] for tx in txs[:limit]]
            
            # Filter out ones we've already seen
            new_txids = [txid for txid in txids if txid not in self.seen_txids]
            
            # Mark as seen
            self.seen_txids.update(new_txids)
            
            return new_txids
            
        except Exception as e:
            print(f"❌ Error fetching recent txids: {e}")
            return []
    
    def get_tx_hex(self, txid: str) -> Optional[str]:
        """Get raw transaction hex"""
        try:
            r = requests.get(f"{self.base_url}/tx/{txid}/hex", timeout=10)
            r.raise_for_status()
            return r.text.strip()
        except Exception as e:
            print(f"❌ Error fetching tx {txid}: {e}")
            return None
    
    def get_prev_tx_hex(self, txid: str, vout_idx: int) -> Optional[str]:
        """Get the previous transaction hex (to find input values)"""
        try:
            # First get the spending tx to find the prev txid
            r = requests.get(f"{self.base_url}/tx/{txid}", timeout=10)
            r.raise_for_status()
            tx_data = r.json()
            
            if not tx_data['vin']:
                return None
            
            # Get the first input's previous txid
            prev_txid = tx_data['vin'][vout_idx]['txid']
            return self.get_tx_hex(prev_txid)
            
        except Exception as e:
            print(f"❌ Error fetching prev tx: {e}")
            return None

if __name__ == "__main__":
    # Test it!
    print("🔍 Testing Blockstream API...")
    api = BlockstreamAPI()
    
    txids = api.get_recent_txids(limit=5)
    print(f"\n✅ Found {len(txids)} recent transactions:")
    
    for txid in txids[:3]:
        print(f"  - {txid[:16]}...")
        hex_data = api.get_tx_hex(txid)
        if hex_data:
            print(f"    ✅ Got hex data ({len(hex_data)} chars)")