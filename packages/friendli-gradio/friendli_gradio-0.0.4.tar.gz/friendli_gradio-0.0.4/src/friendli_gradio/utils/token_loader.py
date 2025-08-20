"""
Utility to load FRIENDLI_TOKEN from multiple places in a safe, cross-environment way.

Priority (default):
 1. Google Colab secrets (google.colab.userdata)
 2. Environment variable FRIENDLI_TOKEN
 3. Docker secret file /run/secrets/FRIENDLI_TOKEN
 4. User config file ~/.config/friendli/token
 5. OS keyring (optional; requires 'keyring' package)

This module caches the Colab lookup per-session and uses a Lock to avoid
concurrent access issues.
"""
from pathlib import Path
import os
import warnings
from threading import Lock
from typing import Optional

_COLAB_CHECKED = False
_COLAB_LOCK = Lock()
_COLAB_TOKEN: Optional[str] = None


def get_friendli_token() -> Optional[str]:
    """
    Return the FRIENDLI token found in the current environment following the
    priority described above, or None if no token found.
    """
    return (
        _get_token_from_google_colab()
        or _get_token_from_env()
        or _get_token_from_docker_secret()
        or _get_token_from_config_file()
        or _get_token_from_keyring()
    )


def _clean_token(token: Optional[str]) -> Optional[str]:
    if token is None:
        return None
    # strip whitespace and newlines; empty -> None
    return token.replace("\r", "").replace("\n", "").strip() or None


def _get_token_from_env() -> Optional[str]:
    return _clean_token(os.environ.get("FRIENDLI_TOKEN"))


def _get_token_from_docker_secret() -> Optional[str]:
    # Common docker secret path; customize as needed
    secret_path = Path("/run/secrets/FRIENDLI_TOKEN")
    try:
        if secret_path.exists():
            return _clean_token(secret_path.read_text())
    except Exception:
        # don't fail hard on IO errors; just skip
        pass
    return None


def _get_token_from_config_file() -> Optional[str]:
    cfg = Path.home() / ".config" / "friendli" / "token"
    try:
        if cfg.exists():
            return _clean_token(cfg.read_text())
    except Exception:
        pass
    return None


def _get_token_from_keyring() -> Optional[str]:
    try:
        import keyring  # optional dependency
    except Exception:
        return None
    try:
        # service name and username can be adjusted
        token = keyring.get_password("friendli", "friendli_token")
        return _clean_token(token)
    except Exception:
        return None


def _get_token_from_google_colab() -> Optional[str]:
    """
    If running in Google Colab and the user defined a secret named FRIENDLI_TOKEN,
    try to retrieve it using google.colab.userdata.get("FRIENDLI_TOKEN").

    Access to user secrets may prompt the user; we cache the result for the session
    and only attempt once to avoid repeated popups.
    """
    # Fast checks: try import-only to detect colab environment quickly
    try:
        # is Google Colab if google.colab exists
        import google.colab  # type: ignore
    except Exception:
        return None

    # If we are in Colab, try to get userdata; but it's not thread-safe so lock
    from google.colab import userdata  # type: ignore

    global _COLAB_CHECKED, _COLAB_TOKEN
    with _COLAB_LOCK:
        if _COLAB_CHECKED:
            return _COLAB_TOKEN
        try:
            token = userdata.get("FRIENDLI_TOKEN")
            _COLAB_TOKEN = _clean_token(token)
        except AttributeError:
            # userdata API is different or not available
            _COLAB_TOKEN = None
        except userdata.NotebookAccessError:
            # user refused to grant access to the secret for this notebook
            warnings.warn(
                "Access to Colab secret 'FRIENDLI_TOKEN' was not granted for this notebook. "
                "You won't be prompted again in this session."
            )
            _COLAB_TOKEN = None
        except userdata.SecretNotFoundError:
            # secret not defined
            _COLAB_TOKEN = None
        except Exception:
            # generic Colab error: don't raise; just skip and optionally warn
            warnings.warn(
                "Error while reading Colab secret 'FRIENDLI_TOKEN'; skipping.")
            _COLAB_TOKEN = None

        _COLAB_CHECKED = True
        return _COLAB_TOKEN


# Example usage
if __name__ == "__main__":
    token = get_friendli_token()
    if token:
        print("Found token (hidden).")  # don't print token value
    else:
        print("No FRIENDLI_TOKEN found.")
