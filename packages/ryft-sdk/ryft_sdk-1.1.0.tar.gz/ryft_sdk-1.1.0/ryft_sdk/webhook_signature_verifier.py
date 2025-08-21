import hashlib
import hmac


class WebhookSignatureVerifier:
    def is_valid(self, secret: str, signature: str, payload: str) -> bool:
        return self._hmac_sha256(secret, payload) == signature

    def _hmac_sha256(self, secret: str, payload: str) -> str:
        secret_bytes = secret.encode("ascii")
        payload_bytes = payload.encode("utf-8")
        hmac_hash = hmac.new(secret_bytes, payload_bytes, hashlib.sha256)
        return hmac_hash.hexdigest()
