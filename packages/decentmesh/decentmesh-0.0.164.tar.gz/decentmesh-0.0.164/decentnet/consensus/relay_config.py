import os

RELAY_FREQUENCY_DB_ALIVE_UPDATE = 100  # Number of blocks needed to update info about connected node in DB
RELAY_DEFAULT_SIGNING_KEY_ID = int(os.getenv("RELAY_DEFAULT_SIGNING_KEY_ID", 1))
RELAY_DEFAULT_ENCRYPTION_KEY_ID = int(os.getenv("RELAY_DEFAULT_ENCRYPTION_KEY_ID", 4))
