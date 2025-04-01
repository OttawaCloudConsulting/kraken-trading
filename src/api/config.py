import os
from datetime import datetime

# Only load .env in development environments
if os.getenv("USE_DOTENV", "true").lower() == "true":
    from dotenv import load_dotenv
    load_dotenv()

# Retrieve API expiry date
KRAKEN_API_EXPIRY = os.getenv("KRAKEN_API_EXPIRY")
KRAKEN_API_KEY = os.getenv("KRAKEN_API_KEY")
KRAKEN_API_SECRET = os.getenv("KRAKEN_API_SECRET")

# Ensure keys are loaded properly
if not KRAKEN_API_KEY or not KRAKEN_API_SECRET:
    raise ValueError("❌ Kraken API keys not found. Please set them as environment variables.")

# Convert expiry date to datetime object
if KRAKEN_API_EXPIRY:
    try:
        expiry_date = datetime.strptime(KRAKEN_API_EXPIRY, "%Y-%m-%d")
        print(f"✅ API Key expires on: {expiry_date.strftime('%B %d, %Y')}")
    except ValueError:
        raise ValueError("❌ Invalid date format in .env. Use YYYY-MM-DD.")
else:
    print("⚠️ No expiry date set for API Key.")

def mongo_uri():
    """
    Builds and returns the MongoDB URI using environment variables.
    """
    username = os.getenv("MONGO_USER")
    password = os.getenv("MONGO_PASS")
    if username and password:
        return f"mongodb://{username}:{password}@mongodb-service:27017"
    return None

# MongoDB Configuration
MONGO_URI = mongo_uri() or os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "kraken_data")

# Enable or Disable MongoDB Storage
STORE_IN_MONGODB = os.getenv("STORE_IN_MONGODB", "false").lower() == "true"
