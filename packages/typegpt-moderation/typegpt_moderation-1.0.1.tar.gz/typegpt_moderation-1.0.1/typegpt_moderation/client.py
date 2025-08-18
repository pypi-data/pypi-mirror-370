# typegpt_moderation/client.py

import httpx
import base64
import os
from typing import Optional, Union, List, Dict, Any

from .models import ModerationResponse

class ModerationAPIError(Exception):
    """Custom exception for API errors."""
    def __init__(self, status_code: int, detail: Any):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"API Error {status_code}: {detail}")

class ModerationClient:
    """
    A client for interacting with the TypeGPT Multimodal Moderation API.
    
    This client can be used as a context manager:
    with ModerationClient() as client:
        result = client.moderate(text="example")
    """

    def __init__(self, base_url: str = "https://mono.typegpt.net", timeout: int = 180):
        if not base_url:
            raise ValueError("base_url cannot be empty.")
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/v3/moderations"
        self._client = httpx.Client(timeout=timeout)

    def _prepare_media(self, source: Union[str, bytes]) -> str:
        if isinstance(source, bytes):
            return base64.b64encode(source).decode('utf-8')
        if isinstance(source, str):
            if os.path.exists(source) and os.path.isfile(source):
                with open(source, "rb") as f:
                    return base64.b64encode(f.read()).decode('utf-8')
            return source
        raise TypeError(f"Unsupported media source type: {type(source)}")

    def moderate(
        self,
        text: Optional[Union[str, List[str]]] = None,
        image: Optional[Union[str, bytes]] = None,
        video: Optional[Union[str, bytes]] = None,
        voice: Optional[Union[str, bytes]] = None,
        language: str = "auto",
        video_frame_count: int = 8
    ) -> ModerationResponse:
        if not any([text, image, video, voice]):
            raise ValueError('At least one of `text`, `image`, `video`, or `voice` must be provided.')

        payload: Dict[str, Any] = {
            "model": "nai-moderation-latest",
            "language": language,
            "video_frame_count": video_frame_count,
        }

        if text: payload["input"] = text
        if image: payload["image"] = self._prepare_media(image)
        if video: payload["video"] = self._prepare_media(video)
        if voice: payload["voice"] = self._prepare_media(voice)

        try:
            response = self._client.post(self.api_url, json=payload)
            response.raise_for_status()
            return ModerationResponse.parse_obj(response.json())
        except httpx.HTTPStatusError as e:
            raise ModerationAPIError(e.response.status_code, e.response.json()) from e
        except httpx.RequestError as e:
            raise ModerationAPIError(500, f"Request failed: {e}") from e

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()