import tweepy
import os
from typing import Optional

class TwitterPublisher:
    """Posts tweets about atomic swaps"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.client = None
        
        if not dry_run:
            self._init_client()
    
    def _init_client(self):
        """Initialize Twitter API client"""
        consumer_key = os.getenv("X_CONSUMER_KEY")
        consumer_secret = os.getenv("X_CONSUMER_SECRET")
        access_token = os.getenv("X_ACCESS_TOKEN")
        access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")
        
        if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
            raise ValueError("Missing Twitter API credentials in .env file!")
        
        # Create client
        self.client = tweepy.Client(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
        
        print("✅ Twitter client initialized")
    
    def send(self, message: str) -> bool:
        """Send a tweet"""
        if self.dry_run:
            print("\n" + "="*60)
            print("🔵 DRY RUN - Would have tweeted:")
            print("="*60)
            print(message)
            print("="*60 + "\n")
            return True
        
        try:
            response = self.client.create_tweet(text=message)
            tweet_id = response.data['id']
            print(f"✅ Tweet posted! ID: {tweet_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to tweet: {e}")
            return False

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    # Test in dry-run mode
    print("🐦 Testing Twitter publisher (DRY RUN)...")
    publisher = TwitterPublisher(dry_run=True)
    
    test_message = """BTC↔XMR atomic swap (candidate)
txid: abc123def456
amount: 0.04200000 BTC ≈ 10.9941 XMR (current rate)
step: REDEEM
https://mempool.space/tx/abc123def456"""
    
    publisher.send(test_message)
    print("\n✅ Twitter publisher test complete!")