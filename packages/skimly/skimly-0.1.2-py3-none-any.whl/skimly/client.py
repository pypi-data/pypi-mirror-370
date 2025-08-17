from __future__ import annotations
import os, json, time, requests, hashlib
from typing import Any, Dict, List, Literal, Optional
from .errors import SkimlyError

Provider = Literal['openai','anthropic']
Role = Literal['system','user','assistant']

# simple in-process cache
_blob_cache: Dict[str, str] = {}

class Skimly:
    def __init__(self, key: str, base: Optional[str] = None, timeout: int = 30, retries: int = 2):
        if not key:
            raise SkimlyError("SKIMLY key required", 401)
        self.base = (base or "http://localhost:3000").rstrip("/")
        self.key = key
        self.timeout = timeout
        self.retries = retries
        self._sess = requests.Session()

    @classmethod
    def from_env(cls) -> "Skimly":
        base = os.getenv("SKIMLY_BASE", "http://localhost:3000")
        key = os.getenv("SKIMLY_KEY")
        if not key:
            raise SkimlyError("SKIMLY_KEY missing", 401)
        return cls(key=key, base=base)

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base}{path}"
        last_exc = None
        for attempt in range(self.retries + 1):
            try:
                r = self._sess.post(
                    url,
                    headers={"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"},
                    data=json.dumps(payload),
                    timeout=self.timeout
                )
                if r.status_code >= 400:
                    raise SkimlyError(f"HTTP {r.status_code} {r.reason}", r.status_code, data=r.text)
                return r.json()
            except (requests.Timeout, requests.ConnectionError) as e:
                last_exc = e
                if attempt == self.retries:
                    raise
                time.sleep(0.2 * (2 ** attempt))
        if last_exc:
            raise last_exc
        raise SkimlyError("Unknown request error")

    def create_blob(self, content: str, mime_type: str = "text/plain") -> str:
        j = self._post("/api/blobs", {"content": content, "mime_type": mime_type})
        if "blob_id" not in j:
            raise SkimlyError("missing blob_id in response")
        return j["blob_id"]

    def create_blob_if_changed(self, content: str, mime_type: str = "text/plain") -> str:
        h = hashlib.sha256(content.encode()).hexdigest()
        cached = _blob_cache.get(h)
        if cached:
            return cached
        blob_id = self.create_blob(content, mime_type)
        _blob_cache[h] = blob_id
        return blob_id

    def chat(self, provider: Provider, model: str, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self._post("/api/chat", {"provider": provider, "model": model, "messages": messages})
