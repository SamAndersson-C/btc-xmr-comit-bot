# BTC↔XMR COMIT Atomic Swap Bot 🤖

A Twitter bot that detects and tweets about Bitcoin transactions performing COMIT atomic swaps with Monero.

## Features

- ✅ Detects HTLC (Hash Time-Locked Contract) transactions on Bitcoin
- ✅ Tracks swap steps: LOCK, REDEEM, REFUND
- ✅ Calculates BTC↔XMR exchange rate in real-time
- ✅ Posts to Twitter automatically
- ✅ Object-oriented design (easy to adapt to Bitcoin forks)
- ✅ Multi-platform notifications via Apprise

## Setup

1. Clone and install:
```bash
git clone <your-repo>
cd btc-xmr-comit-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Configure:
```bash
cp .env.example .env
# Edit .env with your Twitter API keys
```

3. Run:
```bash
python bot/app.py
```

## License

MIT