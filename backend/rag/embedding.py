import asyncio
import logging
import time
from typing import Any, List

from google import genai
from google.genai.errors import ClientError
from llama_index.core.base.embeddings.base import BaseEmbedding
from pydantic import PrivateAttr

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "gemini-embedding-001"
BATCH_SIZE = 5        # LlamaIndex bir so'rovda nechta chunk yuborishi
RETRY_DELAYS = [5, 15, 30]  # 429 da kutish vaqtlari (soniya)


class GeminiEmbedding(BaseEmbedding):
    """
    google-genai SDK orqali Google Gemini embedding.
    LlamaIndex BaseEmbedding interfeysi bilan mos keladi.
    429 RESOURCE_EXHAUSTED da avtomatik retry qiladi.
    """

    _client: Any = PrivateAttr()

    def __init__(self, api_key: str, model_name: str = DEFAULT_MODEL, **kwargs):
        # embed_batch_size — LlamaIndex bir vaqtda nechta matn yuboradi
        kwargs.setdefault("embed_batch_size", BATCH_SIZE)
        super().__init__(model_name=model_name, **kwargs)
        self._client = genai.Client(api_key=api_key)

    def _call_with_retry(self, texts: List[str]) -> List[List[float]]:
        """429 kelsa RETRY_DELAYS bo'yicha kutib qayta urinadi."""
        for attempt, delay in enumerate(RETRY_DELAYS + [None]):
            try:
                response = self._client.models.embed_content(
                    model=self.model_name,
                    contents=texts,
                )
                return [list(e.values) for e in response.embeddings]
            except ClientError as e:
                if e.status_code == 429 and delay is not None:
                    logger.warning(
                        f"429 kvota limiti — {delay}s kutilmoqda (urinish {attempt + 1}/{len(RETRY_DELAYS)})"
                    )
                    time.sleep(delay)
                else:
                    raise

    def _embed(self, text: str) -> List[float]:
        return self._call_with_retry([text])[0]

    def _embed_batch(self, texts: List[str]) -> List[List[float]]:
        return self._call_with_retry(texts)

    # ── LlamaIndex majburiy metodlari ─────────────────────────────────────

    def _get_query_embedding(self, query: str) -> List[float]:
        return self._embed(query)

    def _get_text_embedding(self, text: str) -> List[float]:
        return self._embed(text)

    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        return self._embed_batch(texts)

    async def _aget_query_embedding(self, query: str) -> List[float]:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._embed, query)

    async def _aget_text_embedding(self, text: str) -> List[float]:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._embed, text)
