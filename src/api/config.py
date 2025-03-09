import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Retrieve API expiry date
KRAKEN_API_EXPIRY = os.getenv("KRAKEN_API_EXPIRY")
KRAKEN_API_KEY = os.getenv("KRAKEN_API_KEY")
KRAKEN_API_SECRET = os.getenv("KRAKEN_API_SECRET")

# Convert expiry date to datetime object
if KRAKEN_API_EXPIRY:
    try:
        expiry_date = datetime.strptime(KRAKEN_API_EXPIRY, "%Y-%m-%d")
        print(f"✅ API Key expires on: {expiry_date.strftime('%B %d, %Y')}")
    except ValueError:
        raise ValueError("❌ Invalid date format in .env. Use YYYY-MM-DD.")
else:
    print("⚠ No expiry date set for API Key.")

# Ensure keys are loaded properly
if not KRAKEN_API_KEY or not KRAKEN_API_SECRET:
    raise ValueError("❌ Kraken API keys not found. Please set them in the .env file.")