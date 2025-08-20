import os

# Local tasks config
PROMETHEUS_HOST = os.getenv("PROMETHEUS_HOST", "127.0.0.1")
PROMETHEUS_PORT = int(os.getenv("PROMETHEUS_PORT", "8135"))

# DB config
# If using sqlite
DB_FILENAME = os.getenv("DB_FILENAME", "main.db")

# If using mysql, this needs to be specified
DB_USER = os.getenv("DB_USER", None)
DB_PASSWORD = os.getenv("DB_PASSWORD", None)
DB_HOST = os.getenv("DB_HOST", None)
DB_PORT = os.getenv("DB_PORT", None)
DB_NAME = os.getenv("DB_NAME", None)

# Construct the connection string
if DB_USER and DB_PASSWORD and DB_HOST and DB_PORT and DB_NAME:
    DATABASE_URL_ASYNC = os.getenv("DATABASE_URL",
                                   f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?timeout=30")
else:
    DATABASE_URL_ASYNC = f"sqlite+aiosqlite:///{DB_FILENAME}?timeout=30"
    DATABASE_URL_SYNC = f"sqlite:///{DB_FILENAME}?timeout=30"
