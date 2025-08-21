from dotenv import dotenv_values

_CONFIG = dotenv_values(".env")

if "APP_JSON_FILENAME" not in _CONFIG:
    _CONFIG["APP_JSON_FILENAME"] = "data/db.json"

if "APP_GRAPHQL_IDE_ENABLE" not in _CONFIG:
    _CONFIG["APP_GRAPHQL_IDE_ENABLE"] = True

DB_JSON_FILENAME = _CONFIG["APP_JSON_FILENAME"]
GRAPHQL_IDE_ENABLE = bool(_CONFIG["APP_GRAPHQL_IDE_ENABLE"])
