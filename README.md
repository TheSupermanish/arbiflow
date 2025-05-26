# ArbiFlow

## Overview

**ArbiFlow** is a fully automated crypto arbitrage trading bot that continuously scans multiple centralized and decentralized exchanges to identify and exploit profitable price discrepancies. Designed for reliability, speed, and transparency, ArbiFlow automates the process of buying low on one exchange and selling high on another—capturing market inefficiencies in real time, with robust fee modeling and advanced opportunity filtering.

---

## Features

- ⚡ **Real-Time Arbitrage:** Monitors price feeds and orderbooks across top CEXs and DEXs (Binance, Gate, KuCoin, OKX, and more)
- 🧮 **Smart Fee & Slippage Modeling:** Executes trades only when after-fee profits are positive, accounting for all base and quote-side exchange fees
- 🤖 **Automated Trading:** Executes buy and sell orders simultaneously across different exchanges for delta-neutral arbitrage
- 📊 **Live Terminal Dashboard:** Visualizes opportunities, spread, and profit/loss with real-time refresh in the terminal
- 🛠️ **Configurable:** Supports custom profit thresholds, trade sizes, and whitelisted pairs/exchanges
- 🛡️ **Robust Error Handling:** Recovers from network/API issues and logs every opportunity and trade
- 🔔 **Optional Alerts:** Telegram notifications for new arbitrage opportunities and profit booking
- 📜 **Detailed Logging:** Tracks all trades, opportunities, and session profit for full transparency

---

## How It Works

1. **Connects to Multiple Exchanges:**  
   Uses the [CCXT](https://github.com/ccxt/ccxt) library for CEXs, and web3 APIs for DEXs (coming soon).
2. **Scans All Order Books:**  
   Fetches real-time bids/asks for target pairs (e.g., BTC/USDT).
3. **Detects Profitable Opportunities:**  
   Calculates after-fee profit using the actual exchange fee schedule and trade size.
4. **Executes Trades:**  
   Places buy and sell orders atomically to lock in the arbitrage spread.
5. **Monitors Balances & Logs Everything:**  
   Provides live feedback and logs each trade for auditing and review.

---

## Getting Started

### Prerequisites

- Python 3.8+
- pip
- API keys for your preferred exchanges (Binance, Gate, KuCoin, etc.)

### Installation

```bash
git clone https://github.com/theidealmanish/arbiflow.git
cd arbiflow
pip install -r requirements.txt
python run.py
```
