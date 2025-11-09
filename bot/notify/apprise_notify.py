import apprise
import os

class ApprisePublisher:
    """Send notifications to multiple platforms (Discord, Telegram, etc.)"""
    
    def __init__(self):
        self.apprise = apprise.Apprise()
        self.enabled = False
        
        # Load targets from environment
        targets = os.getenv("APPRISE_TARGETS", "").strip()
        
        if targets:
            for target in targets.split(","):
                target = target.strip()
                if target:
                    self.apprise.add(target)
                    self.enabled = True
            
            if self.enabled:
                print(f"✅ Apprise enabled with {len(self.apprise)} target(s)")
        else:
            print("ℹ️  Apprise disabled (no APPRISE_TARGETS set)")
    
    def send(self, title: str, message: str) -> bool:
        """Send a notification"""
        if not self.enabled:
            return False
        
        try:
            self.apprise.notify(
                title=title,
                body=message
            )
            print("✅ Apprise notification sent")
            return True
            
        except Exception as e:
            print(f"❌ Apprise failed: {e}")
            return False

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    print("📢 Testing Apprise...")
    publisher = ApprisePublisher()
    
    if publisher.enabled:
        publisher.send(
            "Test Notification",
            "This is a test from the BTC↔XMR bot!"
        )
    else:
        print("ℹ️  Add APPRISE_TARGETS to .env to enable (e.g., discord://webhook_id/webhook_token)")