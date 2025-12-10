"""File I/O with retry logic for cloud sync awareness."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


async def read_with_retry(
    path: Path,
    max_retries: int = 3,
    initial_delay: float = 0.1,
) -> str:
    """Read file content with retry logic for cloud sync delays.

    OneDrive, Dropbox, and Google Drive can cause transient I/O errors
    when files aren't locally cached. This function automatically retries
    with exponential backoff.

    Args:
        path: Path to file to read.
        max_retries: Maximum number of retry attempts.
        initial_delay: Initial delay in seconds before first retry.

    Returns:
        File content as string.

    Raises:
        FileNotFoundError: If file doesn't exist.
        OSError: If file can't be read after all retries.
    """
    delay = initial_delay
    last_error: OSError | None = None

    for attempt in range(max_retries):
        try:
            return path.read_text(encoding="utf-8")
        except OSError as e:
            last_error = e
            if e.errno == 5 and attempt < max_retries - 1:
                if attempt == 0:
                    logger.warning(
                        f"File I/O error reading {path} - retrying. "
                        "This may be due to cloud-synced files (OneDrive, Dropbox, etc.). "
                        "Consider enabling 'Always keep on this device' for the data folder."
                    )
                await asyncio.sleep(delay)
                delay *= 2
            else:
                raise

    raise last_error  # type: ignore[misc]


async def write_with_retry(
    path: Path,
    content: str,
    max_retries: int = 3,
    initial_delay: float = 0.1,
) -> None:
    """Write content to file with retry logic for cloud sync delays.

    Args:
        path: Path to file to write.
        content: Content to write.
        max_retries: Maximum number of retry attempts.
        initial_delay: Initial delay in seconds before first retry.

    Raises:
        OSError: If file can't be written after all retries.
    """
    delay = initial_delay
    last_error: OSError | None = None

    for attempt in range(max_retries):
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            return
        except OSError as e:
            last_error = e
            if e.errno == 5 and attempt < max_retries - 1:
                if attempt == 0:
                    logger.warning(
                        f"File I/O error writing to {path} - retrying. "
                        "This may be due to cloud-synced files (OneDrive, Dropbox, etc.). "
                        "Consider enabling 'Always keep on this device' for the data folder."
                    )
                await asyncio.sleep(delay)
                delay *= 2
            else:
                raise

    raise last_error  # type: ignore[misc]
