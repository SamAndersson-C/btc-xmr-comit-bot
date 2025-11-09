from decimal import Decimal

class TweetFormatter:
    """Formats atomic swap data into tweets"""
    
    @staticmethod
    def format_swap_tweet(
        txid: str,
        btc_amount: Decimal,
        xmr_amount: Decimal,
        step: str
    ) -> str:
        """Format a tweet about an atomic swap"""
        return (
            f"BTC↔XMR atomic swap (candidate)\n"
            f"txid: {txid}\n"
            f"amount: {btc_amount:.8f} BTC ≈ {xmr_amount:.4f} XMR (current rate)\n"
            f"step: {step}\n"
            f"https://mempool.space/tx/{txid}"
        )

if __name__ == "__main__":
    # Test it!
    formatter = TweetFormatter()
    
    tweet = formatter.format_swap_tweet(
        txid="abc123def456789",
        btc_amount=Decimal("0.042"),
        xmr_amount=Decimal("10.9941"),
        step="REDEEM"
    )
    
    print("📝 Sample tweet:")
    print(tweet)