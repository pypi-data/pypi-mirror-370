import hashlib

# simple in-process cache
_blob_cache: dict[str, str] = {}

def sha256_hex(data: str) -> str:
    """Generate SHA256 hash of string data"""
    return hashlib.sha256(data.encode()).hexdigest()

def cache_get_blob_id(hash_value: str) -> str | None:
    """Get cached blob ID for a hash"""
    return _blob_cache.get(hash_value)

def cache_set_blob_id(hash_value: str, blob_id: str) -> None:
    """Set cached blob ID for a hash"""
    _blob_cache[hash_value] = blob_id
