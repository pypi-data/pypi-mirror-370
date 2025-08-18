import datetime as _dt
import mimetypes
import os
import pathlib
import time as _time
from typing import IO, Iterable, TypedDict

import requests
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Environment variables inside the kernel VM
# ---------------------------------------------------------------------------

TOKEN_ENV = "LUMERA_TOKEN"
BASE_URL_ENV = "LUMERA_BASE_URL"
ENV_PATH = "/root/.env"

# Load variables from /root/.env if it exists (and also current dir .env)
load_dotenv(override=False)  # Local .env (no-op in prod)
load_dotenv(ENV_PATH, override=False)


# Determine API base URL ------------------------------------------------------

_default_api_base = "https://app.lumerahq.com/api"
API_BASE = os.getenv(BASE_URL_ENV, _default_api_base).rstrip("/")
MOUNT_ROOT_ENV = "LUMERA_MOUNT_ROOT"
DEFAULT_MOUNT_ROOT = "/lumera-files"  # backward compatible default
MOUNT_ROOT = os.getenv(MOUNT_ROOT_ENV, DEFAULT_MOUNT_ROOT)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _ensure_token() -> str:
    """Return the personal Lumera token, loading /root/.env if necessary."""

    token = os.getenv(TOKEN_ENV)
    if token:
        return token

    raise RuntimeError(
        f"{TOKEN_ENV} environment variable not set (checked environment and {ENV_PATH})"
    )


# ---------------------------------------------------------------------------
# Provider-agnostic access-token retrieval
# ---------------------------------------------------------------------------


# _token_cache maps provider
# without an explicit expiry (e.g. API keys) we store `float('+inf')` so that
# they are never considered stale.
# Map provider -> (token, expiry)
_token_cache: dict[str, tuple[str, float]] = {}

# ``expires_at`` originates from the Lumera API and may be one of several
# formats: epoch seconds (``int``/``float``), an RFC 3339 / ISO-8601 string, or
# even ``None``. We therefore accept ``Any`` and normalise it internally.


# Accept multiple formats returned by the API (epoch seconds or ISO-8601), or
# ``None`` when the token never expires.


def _parse_expiry(expires_at: int | float | str | None) -> float:
    """Convert `expires_at` from the API (may be ISO8601 or epoch) to epoch seconds.

    Returns +inf if `expires_at` is falsy/None.
    """

    if not expires_at:
        return float("inf")

    if isinstance(expires_at, (int, float)):
        return float(expires_at)

    # Assume RFC 3339 / ISO 8601 string.
    if isinstance(expires_at, str):
        if expires_at.endswith("Z"):
            expires_at = expires_at[:-1] + "+00:00"
        return _dt.datetime.fromisoformat(expires_at).timestamp()

    raise TypeError(f"Unsupported expires_at format: {type(expires_at)!r}")


def _fetch_access_token(provider: str) -> tuple[str, float]:
    """Call the Lumera API to obtain a valid access token for *provider*."""

    provider = provider.lower().strip()
    if not provider:
        raise ValueError("provider is required")

    token = _ensure_token()

    url = f"{API_BASE}/connections/{provider}/access-token"
    headers = {"Authorization": f"token {token}"}

    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()

    data = resp.json()
    access_token = data.get("access_token")
    expires_at = data.get("expires_at")

    if not access_token:
        raise RuntimeError(f"Malformed response from Lumera when fetching {provider} access token")

    expiry_ts = _parse_expiry(expires_at)
    return access_token, expiry_ts


def get_access_token(provider: str, min_valid_seconds: int = 900) -> str:
    """Return a cached access token for *provider* valid
    *min_valid_seconds*.

       Automatically refreshes tokens via the Lumera API when they are missing or
       close to expiry.  For tokens without an expiry (API keys) the first value
       is cached indefinitely.
    """

    global _token_cache

    provider = provider.lower().strip()
    if not provider:
        raise ValueError("provider is required")

    now = _time.time()

    cached = _token_cache.get(provider)
    if cached is not None:
        access_token, expiry_ts = cached
        if (expiry_ts - now) >= min_valid_seconds:
            return access_token

    # (Re)fetch from server
    access_token, expiry_ts = _fetch_access_token(provider)
    _token_cache[provider] = (access_token, expiry_ts)
    return access_token


# Backwards-compatibility wrapper ------------------------------------------------


def get_google_access_token(min_valid_seconds: int = 900) -> str:
    """Legacy helper kept for old notebooks
    delegates to get_access_token."""

    return get_access_token("google", min_valid_seconds=min_valid_seconds)


# ---------------------------------------------------------------------------
# Unified FileRef helpers
# ---------------------------------------------------------------------------


class FileRef(TypedDict, total=False):
    scope: str
    id: str
    name: str
    path: str
    run_path: str
    object_name: str
    mime: str
    size: int


def resolve_path(file_or_path: str | FileRef) -> str:
    """Return an absolute path string for a FileRef or path-like input.

    Accepts:
      - str paths (returned as-is)
      - dicts with keys like {"path": "/..."} or {"run_path": "/..."}
    """

    if isinstance(file_or_path, str):
        return file_or_path
    if isinstance(file_or_path, dict):
        if "path" in file_or_path and isinstance(file_or_path["path"], str):
            return file_or_path["path"]
        if "run_path" in file_or_path and isinstance(file_or_path["run_path"], str):
            return file_or_path["run_path"]
    raise TypeError("Unsupported file_or_path; expected str or dict with 'path'/'run_path'")


def open_file(
    file_or_path: str | FileRef,
    mode: str = "r",
    **kwargs: object,
) -> IO[str] | IO[bytes]:
    """Open a file from a FileRef or absolute path inside the mount root.

    Usage:
        with open_file(file_ref, 'r') as f:
            data = f.read()
    """

    p = resolve_path(file_or_path)
    return open(p, mode, **kwargs)


def to_filerefs(
    values: Iterable[str | FileRef],
    scope: str,
    id: str,
) -> list[FileRef]:
    """Convert a list of strings or partial dicts into FileRef-like dicts.

    This is a helper for tests/fixtures; it does not perform storage lookups.
    If a value is a string, it is assumed to be an absolute path under the mount root.
    """

    out: list[FileRef] = []
    for v in values:
        if isinstance(v, str):
            name = os.path.basename(v)
            object_name = f"{scope}/{id}/{name}"
            out.append(
                {
                    "scope": scope,
                    "id": id,
                    "name": name,
                    "path": v,
                    "object_name": object_name,
                }
            )
        elif isinstance(v, dict):
            # Fill minimal fields if missing
            name = v.get("name") or os.path.basename(v.get("path") or v.get("run_path") or "")
            path = v.get("path") or v.get("run_path") or ""
            object_name = v.get("object_name") or f"{scope}/{id}/{name}"
            out.append(
                {
                    "scope": v.get("scope", scope),
                    "id": v.get("id", id),
                    "name": name,
                    "path": path,
                    "object_name": object_name,
                    **{k: v[k] for k in ("mime", "size") if k in v},
                }
            )
        else:
            raise TypeError("values must contain str or dict entries")
    return out


# ---------------------------------------------------------------------------
# Document upload helper (unchanged apart from minor refactoring)
# ---------------------------------------------------------------------------


def _pretty_size(size: int) -> str:
    """Return *size* in bytes as a human-readable string (e.g. "1.2 MB").

    Iteratively divides by 1024 and appends the appropriate unit all the way up
    to terabytes.
    """

    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f} {unit}" if unit != "B" else f"{size} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def _upload_session_file(file_path: str, session_id: str) -> dict:
    """Upload file into the current Playground session's file space."""

    token = _ensure_token()
    path = pathlib.Path(file_path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(path)

    filename = path.name
    size = path.stat().st_size
    mimetype = mimetypes.guess_type(filename)[0] or "application/octet-stream"

    headers = {"Authorization": f"token {token}", "Content-Type": "application/json"}

    # 1) Get signed upload URL
    resp = requests.post(
        f"{API_BASE}/sessions/{session_id}/files/upload-url",
        json={"filename": filename, "content_type": mimetype, "size": size},
        headers=headers,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    upload_url: str = data["upload_url"]
    notebook_path: str = data.get("notebook_path", "")

    # 2) Upload bytes
    with open(path, "rb") as fp:
        put = requests.put(upload_url, data=fp, headers={"Content-Type": mimetype}, timeout=300)
        put.raise_for_status()

    # 3) Optionally enable docs (idempotent; ignore errors)
    try:
        requests.post(
            f"{API_BASE}/sessions/{session_id}/enable-docs",
            headers=headers,
            timeout=15,
        )
    except Exception:
        pass

    return {"name": filename, "notebook_path": notebook_path}


def _upload_agent_run_file(file_path: str, run_id: str) -> dict:
    """Upload file into the current Agent Run's file space."""

    token = _ensure_token()
    path = pathlib.Path(file_path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(path)

    filename = path.name
    size = path.stat().st_size
    mimetype = mimetypes.guess_type(filename)[0] or "application/octet-stream"

    headers = {"Authorization": f"token {token}", "Content-Type": "application/json"}

    # 1) Get signed upload URL for the agent run
    resp = requests.post(
        f"{API_BASE}/agent-runs/{run_id}/files/upload-url",
        json={"filename": filename, "content_type": mimetype, "size": size},
        headers=headers,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    upload_url = data["upload_url"]

    # Prefer returning the structured FileRef if available
    file_ref = data.get("file") if isinstance(data, dict) else None

    # 2) Upload bytes
    with open(path, "rb") as fp:
        put = requests.put(upload_url, data=fp, headers={"Content-Type": mimetype}, timeout=300)
        put.raise_for_status()

    # 3) Return a minimal record, preferring the backend-provided FileRef
    if isinstance(file_ref, dict):
        return file_ref
    # Fallback to a compact shape similar to session uploads
    run_path = (
        data.get("run_path") or data.get("path") or f"/lumera-files/agent_runs/{run_id}/{filename}"
    )
    return {
        "name": filename,
        "run_path": run_path,
        "object_name": data.get("object_name"),
    }


def _upload_document(file_path: str) -> dict:
    """Fallback: Upload file into global Documents collection."""

    token = _ensure_token()
    path = pathlib.Path(file_path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(path)

    filename = path.name
    size = path.stat().st_size
    mimetype = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    pretty = _pretty_size(size)

    headers = {"Authorization": f"token {token}", "Content-Type": "application/json"}
    documents_base = f"{API_BASE}/documents"

    # 1) Create
    resp = requests.post(
        documents_base,
        json={
            "title": filename,
            "content": f"File to be uploaded: {filename} ({pretty})",
            "type": mimetype.split("/")[-1],
            "status": "uploading",
        },
        headers=headers,
        timeout=30,
    )
    resp.raise_for_status()
    doc = resp.json()
    doc_id = doc["id"]

    # 2) Signed URL
    resp = requests.post(
        f"{documents_base}/{doc_id}/upload-url",
        json={"filename": filename, "content_type": mimetype, "size": size},
        headers=headers,
        timeout=30,
    )
    resp.raise_for_status()
    upload_url: str = resp.json()["upload_url"]

    # 3) PUT bytes
    with open(path, "rb") as fp:
        put = requests.put(upload_url, data=fp, headers={"Content-Type": mimetype}, timeout=300)
        put.raise_for_status()

    # 4) Finalize
    resp = requests.put(
        f"{documents_base}/{doc_id}",
        json={
            "status": "uploaded",
            "content": f"Uploaded file: {filename} ({pretty})",
        },
        headers=headers,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def save_to_lumera(file_path: str) -> dict:
    """Upload *file_path* to the current context.

    Priority:
      1) If running inside an Agent executor (LUMERA_RUN_ID), upload to that run
      2) Else if running in Playground (LUMERA_SESSION_ID), upload to the session
      3) Else, upload to global Documents
    """

    run_id = os.getenv("LUMERA_RUN_ID", "").strip()
    if run_id:
        return _upload_agent_run_file(file_path, run_id)

    session_id = os.getenv("LUMERA_SESSION_ID", "").strip()
    if session_id:
        return _upload_session_file(file_path, session_id)
    return _upload_document(file_path)
