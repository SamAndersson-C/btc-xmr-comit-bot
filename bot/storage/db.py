import sqlite3
from typing import Optional
import os

class Store:
    """Simple SQLite database to track what we've already posted"""
    
    def __init__(self, db_path: str = "bot.db"):
        self.db_path = db_path
        self.conn = None
        self._init_db()
    
    def _init_db(self):
        """Create the database and tables if they don't exist"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = self.conn.cursor()
        
        # Table to track posted transactions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posted (
                txid TEXT NOT NULL,
                step TEXT NOT NULL,
                posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (txid, step)
            )
        """)
        
        self.conn.commit()
        print(f"✅ Database ready: {self.db_path}")
    
    def already_posted(self, txid: str, step: str) -> bool:
        """Check if we've already posted this txid+step combo"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT 1 FROM posted WHERE txid = ? AND step = ?",
            (txid, step)
        )
        return cursor.fetchone() is not None
    
    def mark_posted(self, txid: str, step: str):
        """Mark a transaction as posted"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO posted (txid, step) VALUES (?, ?)",
                (txid, step)
            )
            self.conn.commit()
            print(f"✅ Marked as posted: {txid[:16]}... ({step})")
        except sqlite3.IntegrityError:
            # Already exists, that's fine
            pass
    
    def get_stats(self) -> dict:
        """Get some stats about what we've posted"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM posted")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT step, COUNT(*) FROM posted GROUP BY step")
        by_step = dict(cursor.fetchall())
        
        return {"total": total, "by_step": by_step}
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()

if __name__ == "__main__":
    # Test it!
    print("🗄️  Testing database...")
    
    # Clean up any old test db
    if os.path.exists("test.db"):
        os.remove("test.db")
    
    store = Store("test.db")
    
    # Test marking as posted
    store.mark_posted("abc123", "REDEEM")
    store.mark_posted("abc123", "REFUND")
    store.mark_posted("xyz789", "LOCK")
    
    # Test checking
    print(f"Is abc123/REDEEM posted? {store.already_posted('abc123', 'REDEEM')}")
    print(f"Is abc123/LOCK posted? {store.already_posted('abc123', 'LOCK')}")
    
    # Get stats
    stats = store.get_stats()
    print(f"\n📊 Stats: {stats}")
    
    store.close()
    print("\n✅ Database test passed!")