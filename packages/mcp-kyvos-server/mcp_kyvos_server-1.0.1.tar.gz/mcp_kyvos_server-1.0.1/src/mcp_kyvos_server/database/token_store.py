import time
import datetime
from typing import Any, Dict, Optional
from peewee import *
from .db import UserToken, db
from mcp_kyvos_server.utils.logging import setup_logger

logger, log_path = setup_logger()

# ------------------------
# Helper Functions
# ------------------------

def _unix_ts(value: Any) -> int:
    """Convert datetime/str/None → int epoch seconds (None → now)."""
    if value is None:
        return int(time.time())
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        return int(datetime.datetime.fromisoformat(value).timestamp())
    if isinstance(value, datetime.datetime):
        return int(value.timestamp())
    raise ValueError(f"Unsupported timestamp type: {type(value)}")


# ------------------------
# Queries
# ------------------------
def save_tokens(state: str, data: Dict[str, Any]) -> None:
    """
    Insert or update token data for the user identified by `state`.
    `data` is a partial dictionary (only updated fields).
    """
    data = data.copy()
    data["state"] = state  # Primary key

    # Normalize timestamps
    for key in ("bound_issued", "token_issued_at"):
        if key in data and data[key] is not None:
            data[key] = _unix_ts(data[key])

    try:
        with db.atomic():

            # Try to get existing row
            row = UserToken.get_or_none(UserToken.state == state)

            if row:
                for key, value in data.items():
                    if hasattr(row, key):
                        setattr(row, key, value)
                row.updated_at = datetime.datetime.now()
                row.save()
            else:
                UserToken.create(**data)

    except OperationalError as e:
        logger.error(f"Database operation failed for state '{state}': {e}")
        raise 
    except Exception as e:
        logger.error(f"An unexpected error occurred during save_tokens for state '{state}': {e}")
        raise


def get_tokens_state(state: str) -> Optional[Dict[str, Any]]:
    """
    Return a dictionary of tokens for the given `state`, or None if not found.
    """
    try:
        token = UserToken.get_or_none(UserToken.state == state)
        return token.__data__ if token else None
    except OperationalError as e:
        logger.error(f"Database read failed for state '{state}': {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred during get_tokens_state for state '{state}': {e}")
        return None


def get_tokens(email: str) -> Optional[Dict[str, Any]]:
    """Return the most recent set of tokens for a given `email`, or None if not found."""
    try:
        row = (
            UserToken
            .select()
            .where(UserToken.email == email)
            .order_by(UserToken.updated_at.desc())
            .first()
        )
        return row.__data__ if row else None
    except OperationalError as e:
        logger.error(f"Database read failed for email '{email}': {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred during get_tokens for email '{email}': {e}")
        return None


def get_email_by_access_token(access_token: str) -> Optional[str]:
    """Return the email associated with a given access token, or None if not found."""
    try:
        row = (
            UserToken
            .select(UserToken.email)
            .where(UserToken.access_token == access_token)
            .order_by(UserToken.updated_at.desc())
            .first()
        )
        return row.email if row else None
    except OperationalError as e:
        logger.error(f"Database read failed for access token '{access_token}': {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred during get_email_by_access_token for token '{access_token}': {e}")
        return None


def get_email_by_bound_code(bound_code: str) -> Optional[str]:
    """Return the email associated with a given bound code, or None if not found."""
    try:
        row = (
            UserToken
            .select(UserToken.email)
            .where(UserToken.bound_code == bound_code)
            .order_by(UserToken.updated_at.desc())
            .first()
        )
        return row.email if row else None
    except OperationalError as e:
        logger.error(f"Database read failed for bound code '{bound_code}': {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred during get_email_by_bound_code for code '{bound_code}': {e}")
        return None


def get_email_by_client_access_token(client_access_token: str) -> Optional[str]:
    """Return the email associated with a given client's access token, or None if not found."""
    try:
        row = (
            UserToken
            .select(UserToken.email)
            .where(UserToken.client_access_token == client_access_token)
            .order_by(UserToken.updated_at.desc())
            .first()
        )
        return row.email if row else None
    except OperationalError as e:
        logger.error(f"Database read failed for client access token '{client_access_token}': {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred during get_email_by_client_access_token for token '{client_access_token}': {e}")
        return None


def get_email_by_server_refresh_token(refresh_token: str) -> Optional[str]:
    """Return the email associated with a given refresh token, or None if not found."""
    try:
        row = (
            UserToken
            .select(UserToken.email)
            .where(UserToken.refresh_token == refresh_token)
            .order_by(UserToken.updated_at.desc())
            .first()
        )
        return row.email if row else None
    except OperationalError as e:
        logger.error(f"Database read failed for server refresh token '{refresh_token}': {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred during get_email_by_server_refresh_token for token '{refresh_token}': {e}")
        return None


def get_email_by_client_refresh_token(client_refresh_token: str) -> Optional[str]:
    """Return the email associated with a given client's refresh token, or None if not found."""
    try:
        row = (
            UserToken
            .select(UserToken.email)
            .where(UserToken.client_refresh_token == client_refresh_token)
            .order_by(UserToken.updated_at.desc())
            .first()
        )
        return row.email if row else None
    except OperationalError as e:
        logger.error(f"Database read failed for client refresh token '{client_refresh_token}': {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred during get_email_by_client_refresh_token for token '{client_refresh_token}': {e}")
        return None


def update_token_field(email: str, field: str, value: str) -> None:
    """Update a specific token field (e.g., client_access_token) for the most recent record of the given email."""
    allowed_fields = {
        "access_token", "refresh_token", "id_token",
        "client_access_token", "client_refresh_token",
        "auth_code", "bound_issued", "bound_code", 
        "token_issued_at", "expires_in"
    }

    if field not in allowed_fields:
        raise ValueError(f"Invalid field name: {field}")

    if field in ("bound_issued", "token_issued_at"):
        value = _unix_ts(value)

    try:
        with db.atomic():

            # Get the most recent record for the email
            row = (
                UserToken
                .select()
                .where(UserToken.email == email)
                .order_by(UserToken.updated_at.desc())
                .first()
            )

            if row:
                setattr(row, field, value)
                row.updated_at = datetime.datetime.now()
                row.save()
    except OperationalError as e:
        logger.error(f"Database update failed for email '{email}', field '{field}': {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred during update_token_field for email '{email}', field '{field}': {e}")
        raise


def delete_tokens(email: str) -> None:
    """Remove the token bundle for `email` (idempotent)."""
    try:
        with db.atomic():
            (
                UserToken
                .delete()
                .where(UserToken.email == email)
                .execute()
            )
    except OperationalError as e:
        logger.error(f"Database delete failed for email '{email}': {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred during delete_tokens for email '{email}': {e}")
        raise