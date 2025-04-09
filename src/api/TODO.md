# ✅ Kraken Asset Metadata Enrichment Checklist

This checklist tracks the changes required to support enrichment of trade data with `wsname` and `base` using the Kraken Asset Pairs API and MongoDB caching.

## 📦 New Functions

- [x] **`fetch_asset_pairs_from_kraken()`**
  - [x] Call Kraken public endpoint `/0/public/AssetPairs`
  - [x] Return asset metadata dictionary
  - [x] Log request success/failure

- [ ] **`get_asset_pair_info(pair: str)`**
  - [ ] Check if asset pair exists in MongoDB (`kraken_assets` collection)
  - [ ] If missing:
    - [ ] Call `fetch_asset_pairs_from_kraken()`
    - [ ] Insert all asset pairs into MongoDB (insert-if-not-exists)
    - [ ] Retry lookup for `pair`
  - [ ] Return metadata with keys like `wsname`, `base`
  - [ ] Log warnings if fallback to `pair`

- [ ] **`enrich_trades_with_asset_metadata(trades: dict, logger, db_client)`**
  - [ ] For each trade:
    - [ ] Look up metadata by `pair`
    - [ ] Append `wsname` and `base` fields to trade
    - [ ] If pair not found, default to original `pair` string
  - [ ] Log enrichment results (errors, defaults, total enriched)

## 🛠️ Modified Functions

- [ ] **`KrakenAPIClient.get_trade_history()`**
  - [ ] After trade retrieval:
    - [ ] Call `enrich_trades_with_asset_metadata()`
    - [ ] Ensure enriched trades are returned/saved

## 🧱 MongoDB Client Enhancements

- [ ] Add `get_asset_pair(pair: str)` to check MongoDB for an asset
- [ ] Add `insert_asset_pairs(asset_dict)` to batch write asset pair data

## 📁 File Update Scope

| File               | Changes                              |
|--------------------|--------------------------------------|
| `api_client.py`     | Modify `get_trade_history()` logic   |
| `mongodb_client.py` | Add new methods for asset metadata  |
| `utils.py` (opt.)   | Helper functions if needed           |

## 🔐 MongoDB Collections

- [ ] **`kraken_assets`**
  - [ ] Stores asset pairs (`pair`, `wsname`, `base`, etc.)
  - [ ] Insert-if-not-exists logic supported

## 🧪 Testing & Validation

- [ ] First run triggers API fetch and MongoDB population
- [ ] Subsequent runs use cached data
- [ ] Error logging when pair not found
- [ ] Verify `wsname` and `base` appear in exported data

---

✔️ Prepared for implementation and integration into existing workflow.

