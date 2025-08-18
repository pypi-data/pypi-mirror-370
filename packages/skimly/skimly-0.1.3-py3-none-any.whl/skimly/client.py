from __future__ import annotations
import os, json, time, requests
from typing import Any, Dict, List, Literal, Optional, Union
from .errors import SkimlyError, SkimlyHTTPError, SkimlyNetworkError
from .utils import cache_get_blob_id, cache_set_blob_id, sha256_hex

Provider = Literal['openai','anthropic']
Role = Literal['system','user','assistant']

class SkimlyClient:
    def __init__(self, key: str, base: Optional[str] = None, timeout_ms: int = 30000, retries: int = 2):
        if not key:
            raise SkimlyError("SKIMLY key required", 401)
        self.base = (base or "http://localhost:3000").rstrip("/")
        self.key = key
        self.timeout = timeout_ms / 1000  # Convert to seconds for requests
        self.retries = retries
        self._sess = requests.Session()

    @classmethod
    def from_env(cls) -> "SkimlyClient":
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
                    # Retry 5xx errors only
                    if r.status_code >= 500 and attempt < self.retries:
                        time.sleep(0.2 * (2 ** attempt))
                        continue
                    raise SkimlyHTTPError(r.status_code, r.reason, r.text)
                return r.json()
            except (requests.Timeout, requests.ConnectionError) as e:
                last_exc = e
                if attempt == self.retries:
                    raise SkimlyNetworkError("Network/timeout error", e)
                time.sleep(0.2 * (2 ** attempt))
        
        if last_exc:
            raise SkimlyNetworkError("Exhausted retries", last_exc)
        raise SkimlyError("Unknown request error")

    def create_blob(self, content: str, mime_type: str = "text/plain") -> Dict[str, str]:
        """Upload large context once; returns { blob_id }"""
        j = self._post("/api/blobs", {"content": content, "mime_type": mime_type})
        if "blob_id" not in j:
            raise SkimlyError("missing blob_id in response")
        return {"blob_id": j["blob_id"]}

    def create_blob_if_new(self, content: str, mime_type: str = "text/plain") -> Dict[str, str]:
        """In-process dedupe: avoid re-uploading identical content this process has already sent"""
        h = sha256_hex(content)
        cached = cache_get_blob_id(h)
        if cached:
            return {"blob_id": cached}
        res = self.create_blob(content, mime_type)
        cache_set_blob_id(h, res["blob_id"])
        return res

    def chat(self, req: Dict[str, Any]) -> Dict[str, Any]:
        """Chat with provider; messages may be string or array of parts ({type:'text'|'pointer', ...})"""
        return self._post("/api/chat", req)

# Alias for backward compatibility
Skimly = SkimlyClient
