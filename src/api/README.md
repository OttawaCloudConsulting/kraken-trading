# Kraken Trade History Retrieval

## Table of Contents

[TOC]

## 📌 Overview

This Python application retrieves **trade history** and **staking rewards**  data from the Kraken exchange, saves it locally in **JSON** and **CSV** formats, and provides structured logging for debugging and analysis.

## 🚀 Features

- Fetches **all historical trade data** from Kraken.
- Retrieve **staking rewards** (excluding fund transfers) via Kraken's ledger entries.
- Saves trade data in **JSON** and **CSV** formats.
- Implements **structured logging**.
- Supports **custom filenames** for exports.
- Includes **data validation & error handling**.
- Designed for future **MongoDB & AWS S3** integrations.

## 🏗️ Architecture Overview

This application follows a structured process for retrieving, processing, and storing trade history and staking rewards.

```mermaid
graph TD;
    A[Trigger] -->|Execute Application| B["Main Script (main.py)"];
    B -->|API Handler| C["API Script (class KrakenAPIClient)"] ;
    C -->|Fetch Trades| D["Kraken API - TradesHistory (def get_trade_history)"];
    C -->|Fetch Staking Rewards| E["Kraken API - Ledgers (def get_staking_rewards)"];
    D -->|Return Trade Data| F[Process Trades];
    E -->|Return Staking Rewards| F["Process Returned Data (data_handler.py)"];
    F -->|Save to File| G["Trade Data JSON/CSV (def save_trades)"];
    F -->|Save to File| H["Reward Data JSON/CSV (def save_staking_rewards)"];
```

## 🛠️ Installation

### Requirements

- Python **3.11**
- Required Python packages:
  - `requests`
  - `python-dotenv`
  - `ccxt`
  - `pymongo`

### Setup Instructions

1. Clone the repository:

   ```sh
   git clone https://github.com/your-repo/kraken-trade-history.git
   cd kraken-trade-history
   ```

2. Create a virtual environment and install dependencies:

   ```sh
   python3 -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Create a `.env` file with Kraken API credentials:

   ```sh
   cp .env.example .env
   ```

4. Edit `.env` and add your Kraken API keys:

   ```ini
   KRAKEN_API_KEY="your_api_key"
   KRAKEN_API_SECRET="your_api_secret"
   KRAKEN_API_EXPIRY="2025-05-30"
   ```

## 📄 Usage Instructions

### Run the Script

```sh
python main.py
```

## Logging & Debugging

- Set logging level via `LOG_LEVEL` in `.env`.
- Logs provide information on:
  - API requests & responses.
  - Number of trades and staking rewards retrieved.
  - File creation success or failure.

### Customize Filename

Pass a custom filename when saving trade history (default is `my_trades_<timestamp>.json` / `.csv`).

## 🔗 API Integration

### TradesHistory

- Uses **Kraken Private API** (`/0/private/TradesHistory`)
- Requires **API Key & Secret** authentication.
- **Response Format:**

  ```json
  {
    "error": [],
    "result": {
      "trades": {
        "TXID123": {
          "ordertxid": "O123",
          "pair": "BTC/USD",
          "time": 1700000000,
          "type": "buy",
          "price": "50000.00",
          "cost": "1000.00",
          "fee": "2.00",
          "vol": "0.02"
        }
      },
      "count": 150
    }
  }
  ```

### Ledgers

- Retrieves **ledger entries**, which include **staking rewards**.
- We filter the results to **only include `type=staking` and `subtype=""`**, excluding staking transfers.
- This ensures **we do not include staking deposits (`spottostaking`) or withdrawals (`stakingtospot`)**.
- **Response Format:**

  ```json
  "error": [],
  "result": {
    "ledger": {
      "L12345": {
        "refid": "RABC1234",
        "time": 1645231234,
        "type": "staking",
        "subtype": "",
        "asset": "ETH2.S",
        "amount": "0.02",
        "balance": "1.5"
      }
    }
  }
  ```

## 🛠️ Function & Purpose Table

| **Function** | **Purpose** |
|-------------|------------|
| `KrakenAPIClient.get_trade_history()` | Fetches historical trades from Kraken. |
| `save_trades(trades, format, location, logger, filename)` | Saves trade data to JSON or CSV. |
| `_save_to_local(trades, format, filename, logger)` | Handles local file storage. |
| `save_staking_rewards()` | Saves staking rewards to JSON/CSV files. |
| `_generate_filename(extension, custom_filename)` | Generates timestamped filenames. |
| `_ensure_output_directory()` | Creates the `outputs/` directory. |

## 📂 Example Logs & Output

### Example Log Output

```log
2025-03-09 19:02:08,734 - INFO - 🚀 Starting Kraken trade history retrieval...
2025-03-09 19:02:08,952 - INFO - ✅ Trade history retrieved successfully.
2025-03-09 19:02:08,957 - INFO - ✅ JSON file saved: outputs/my_trades_1741561328.json (Size: 28.31 KB)
2025-03-09 19:02:08,958 - INFO - ✅ CSV file saved: outputs/my_trades_1741561328.csv (Size: 0.15 KB)
```

### Example JSON Output

### **Trade History (JSON)**

```json
{
  "TX12345": {
    "ordertxid": "OABC1234",
    "pair": "ETH/USD",
    "time": 1645231234,
    "type": "buy",
    "ordertype": "limit",
    "price": "2500.00",
    "cost": "5000.00",
    "fee": "5.00",
    "vol": "2.0"
  }
}
```

### **Staking Rewards (JSON)**

```json
{
  "L12345": {
    "refid": "RABC1234",
    "time": 1645231234,
    "asset": "ETH2.S",
    "amount": "0.02",
    "balance": "1.5"
  }
}
```

### Example CSV Output

```csv
trade_id,ordertxid,pair,time,type,price,cost,fee,vol
TXID123,O123,BTC/USD,1700000000,buy,50000.00,1000.00,2.00,0.02
```

## 🧪 Testing

*(Placeholder for future testing instructions)*

## 🔧 Troubleshooting

### Invalid API Key

```
❌ API Error: ['EAPI:Invalid key']
```

**Solution:** Verify your Kraken API key and secret in `.env`.

### No Trades Found

```
❌ No valid trade records found for CSV export.
```

**Solution:** Check if your Kraken account has trade history.

## 📅 Future Roadmap

- ✅ **Manual extract | tag: v0.1.0** → Will retrieve data manually, format and export to file 
- ❌ **MongoDB Integration** → Store trade data in a NoSQL database.
- ❌ **AWS S3 Storage** → Upload trade history files to cloud storage.
- ❌ **Enhanced Data Analysis** → Generate trade insights and statistics.

---
🚀 **Developed & Maintained by Christian Turner**
