#!/usr/bin/env python3
"""
BTC↔XMR COMIT Atomic Swap Bot
Detects and tweets about Bitcoin atomic swap transactions
"""

import time
import os
from decimal import Decimal
from dotenv import load_dotenv
from bitcoin.core import CTransaction

# Our modules
from bot.ingest.blockstream import BlockstreamAPI
from bot.chain.detector import HTLCDetector, SwapStep
from bot.pricing.rates import RateProvider
from bot.storage.db import Store
from bot.notify.twitter import TwitterPublisher
from bot.notify.apprise_notify import ApprisePublisher
from bot.notify.formatter import TweetFormatter

class AtomicSwapBot:
    """Main bot that coordinates everything"""
    
    def __init__(self, dry_run: bool = True):
        print("🚀 Initializing BTC↔XMR Atomic Swap Bot...\n")
        
        self.dry_run = dry_run
        
        # Initialize components
        self.api = BlockstreamAPI()
        self.detector = HTLCDetector()
        self.rates = RateProvider()
        self.store = Store()
        self.twitter = TwitterPublisher(dry_run=dry_run)
        self.apprise = ApprisePublisher()
        self.formatter = TweetFormatter()
        
        print("\n✅ Bot initialized!\n")
    
    def get_btc_amount(self, tx_hex: str, prev_tx_hex: str = None) -> Decimal:
        """Extract BTC amount from transaction"""
        try:
            tx = CTransaction.deserialize(bytes.fromhex(tx_hex))
            
            # For simplicity, sum all outputs (you can refine this)
            total_sats = sum(vout.nValue for vout in tx.vout)
            return Decimal(total_sats) / Decimal(100_000_000)
            
        except Exception as e:
            print(f"⚠️  Error parsing tx amount: {e}")
            return Decimal("0.01")  # Fallback
    
    def process_transaction(self, txid: str):
        """Process a single transaction"""
        try:
            # Get raw transaction
            tx_hex = self.api.get_tx_hex(txid)
            if not tx_hex:
                return
            
            # Deserialize and detect
            tx = CTransaction.deserialize(bytes.fromhex(tx_hex))
            step, script = self.detector.classify_step(tx)
            
            # Only care about HTLC transactions
            if step == SwapStep.UNKNOWN:
                return
            
            # Check if we've already posted this
            if self.store.already_posted(txid, step.value):
                return
            
            print(f"\n🎯 HTLC DETECTED! {txid[:16]}... ({step.value})")
            
            # Get amounts
            btc_amount = self.get_btc_amount(tx_hex)
            xmr_rate = self.rates.btc_to_xmr()
            xmr_amount = btc_amount * xmr_rate
            
            # Format tweet
            tweet = self.formatter.format_swap_tweet(
                txid=txid,
                btc_amount=btc_amount,
                xmr_amount=xmr_amount,
                step=step.value
            )
            
            # Send notifications
            if self.twitter.send(tweet):
                self.store.mark_posted(txid, step.value)
            
            if self.apprise.enabled:
                self.apprise.send("Atomic Swap Detected", tweet)
            
        except Exception as e:
            print(f"❌ Error processing {txid[:16]}...: {e}")
    
    def run(self, poll_interval: int = 30):
        """Main bot loop"""
        print(f"🔄 Starting bot (polling every {poll_interval}s)")
        print(f"   Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        print(f"   Press Ctrl+C to stop\n")
        
        try:
            while True:
                # Get recent transactions
                txids = self.api.get_recent_txids(limit=50)
                
                if txids:
                    print(f"🔍 Scanning {len(txids)} new transactions...")
                    
                    for txid in txids:
                        self.process_transaction(txid)
                
                # Show stats
                stats = self.store.get_stats()
                print(f"📊 Posted: {stats['total']} swaps ({stats.get('by_step', {})})")
                
                # Wait before next poll
                time.sleep(poll_interval)
                
        except KeyboardInterrupt:
            print("\n\n👋 Bot stopped by user")
            self.store.close()

def main():
    # Load environment variables
    load_dotenv()
    
    # Check if dry run
    dry_run = os.getenv("DRY_RUN", "true").lower() == "true"
    
    # Create and run bot
    bot = AtomicSwapBot(dry_run=dry_run)
    bot.run(poll_interval=30)

if __name__ == "__main__":
    main()