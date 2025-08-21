import os
from peewee import *
from pathlib import Path
import datetime
import platform
import tempfile


# Define the database path
def _default_path() -> Path:
    """Return the default path to store the SQLite DB file."""
    try:
        if platform.system() == "Darwin":  # macOS
            try:
                db_dir = Path.home() / "Library" / "Application Support" / "MCPKyvosServer" / "Database"
            except:
                db_dir = Path.home() / "MCPKyvosServer" / "Database"

        elif platform.system() == "Windows":
            appdata = os.getenv("APPDATA", str(Path.home() / "AppData" / "Roaming"))
            db_dir = Path(appdata) / "mcp_kyvos_server" / "Database"

        else:  # Linux and others
            db_dir = Path.home() / ".mcp_kyvos_server" / "Database"

        db_dir.mkdir(parents=True, exist_ok=True)
        db_path = db_dir / "mcp_kyvos_server_tokens.db"

    except Exception:
        fallback_dir = Path(tempfile.gettempdir()) / "mcp_kyvos_server_db"
        fallback_dir.mkdir(parents=True, exist_ok=True)
        db_path = fallback_dir / "mcp_kyvos_server_tokens.db"

    return db_path


# Public constant: usable by ORM or other modules
DB_PATH: Path = Path(os.environ.get("MCP_KYVOS_DB_PATH", _default_path()))

db = SqliteDatabase(
    DB_PATH, 
    timeout=5,
    check_same_thread=False,
    pragmas={
        'journal_mode': 'wal'
    }
)


class BaseModel(Model):
    class Meta:
        database = db


class UserToken(BaseModel):
    state = CharField(primary_key=True)

    email = CharField(null=True)
    code_verifier = CharField(null=True)
    code_challenge = CharField(null=True)
    client_redirect_uri = CharField(null=True)
    auth_code = CharField(null=True)
    token_issued_at = IntegerField(null=True)
    access_token = CharField(null=True)
    refresh_token = CharField(null=True)
    id_token = CharField(null=True)
    expires_in = IntegerField(null=True)
    bound_issued = IntegerField(null=True)
    bound_code = CharField(null=True)
    client_access_token = CharField(null=True)
    client_refresh_token = CharField(null=True)
    updated_at = TimestampField(default=datetime.datetime.now)


def init_db():
    """
    Initialize the database, create tables if they don't exist,
    and enable WAL (Write-Ahead Logging) mode for better concurrency.
    """
    db.connect()
    db.create_tables([UserToken], safe=True)
    db.close()