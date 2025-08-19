from __future__ import annotations

import json
from io import BytesIO
from typing import TYPE_CHECKING, Any

import requests
from PIL import Image
from polykit import PolyLog

if TYPE_CHECKING:
    from dsbin.wpmusic.configs import WPConfig


class MetadataFetcher:
    """Fetches and prepares metadata for audio tracks."""

    def __init__(self, config: WPConfig):
        self.config = config
        self.logger = PolyLog.get_logger(
            self.__class__.__name__,
            level=self.config.log_level,
            simple=self.config.log_simple,
        )
        self._all_metadata: dict[str, Any] | None = None
        self._cover_data: bytes | None = None

    @property
    def all_metadata(self) -> dict[str, Any]:
        """Lazy-load and cache the metadata."""
        if self._all_metadata is None:
            self._all_metadata, self._cover_data = self._fetch_metadata()
        return self._all_metadata

    @property
    def cover_data(self) -> bytes | None:
        """Lazy-load and cache the cover data."""
        if self._all_metadata is None:
            self._all_metadata, self._cover_data = self._fetch_metadata()
        return self._cover_data

    def _fetch_metadata(self) -> tuple[dict[str, Any], bytes | None]:
        """Retrieve metadata and cover art."""
        self.logger.debug("Fetching metadata from %s", self.config.metadata_url)
        try:
            response = requests.get(self.config.metadata_url, timeout=10)

            # Check if response is successful
            response.raise_for_status()

            # Check if response contains data
            if not response.text:
                self.logger.error("Empty response received from metadata URL.")
                return {}, None

            # Try to parse JSON
            all_metadata = json.loads(response.text)

        except requests.RequestException as e:
            self.logger.error("Failed to fetch metadata: %s", str(e))
            return {}, None
        except json.JSONDecodeError as e:
            self.logger.error("Failed to parse metadata JSON: %s", str(e))
            self.logger.debug(
                "Response content: %s",
                response.text[:100] + "..." if len(response.text) > 100 else response.text,
            )
            return {}, None

        cover_data = None

        if cover_art_url := all_metadata.get("metadata", {}).get("cover_art_url", ""):
            self.logger.debug("Downloading cover art from %s", cover_art_url)
            try:
                cover_data = self._download_cover_art(cover_art_url)
            except Exception as e:
                self.logger.error("Failed to download cover art: %s", str(e))

        return all_metadata, cover_data

    @staticmethod
    def _download_cover_art(url: str) -> bytes | None:
        """Download cover art from the given URL and return the bytes."""
        response = requests.get(url, timeout=10)
        cover_art_bytes = BytesIO(response.content)
        cover_image = Image.open(cover_art_bytes).convert("RGB")
        cover_data = cover_image.resize((800, 800))
        buffered = BytesIO()
        cover_data.save(buffered, format="JPEG")

        return buffered.getvalue()
