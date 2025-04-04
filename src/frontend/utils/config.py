import os

def mongo_uri() -> str:
    """Returns the MongoDB URI from environment variables.

    Prefers explicit MONGODB_URI. Otherwise constructs it from MONGO_USER and MONGO_PASS.
    Logs usage via print statements for basic traceability in frontend usage.
    
    Returns:
        str: MongoDB connection URI.
    """
    explicit_uri = os.getenv("MONGODB_URI")
    if explicit_uri:
        print("🛠️ Using explicit MONGODB_URI from environment.")
        return explicit_uri

    username = os.getenv("MONGO_USER")
    password = os.getenv("MONGO_PASS")

    if not username or not password:
        print("❌ MONGO_USER or MONGO_PASS not set in environment.")
    else:
        print("🛠️ Constructed MongoDB URI from username and password.")
        print(f"MongoDB URI: mongodb://{username}:{password}@mongodb-service:27017")

    return f"mongodb://{username}:{password}@mongodb-service:27017"

# MongoDB Configuration
DB_NAME = os.getenv("DB_NAME", "kraken_data")