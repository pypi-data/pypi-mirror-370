import hmac, hashlib

def verify_skimly_signature(signature: str, raw_body: bytes, secret: str) -> bool:
    """
    Verify Skimly webhook signature.
    signature header format: "v1=<hex>"
    """
    if not signature or not signature.startswith("v1="):
        return False
    expected = "v1=" + hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected)
