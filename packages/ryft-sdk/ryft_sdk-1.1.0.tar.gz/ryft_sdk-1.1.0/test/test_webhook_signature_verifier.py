import unittest
from ryft_sdk.webhook_signature_verifier import WebhookSignatureVerifier


class TestWebhookSignatureVerifier(unittest.TestCase):
    """Unit tests for WebhookSignatureVerifier."""

    def setUp(self):
        self.verifier = WebhookSignatureVerifier()

    def test_is_valid_should_return_false_when_signature_is_invalid(self):
        payload = '{"amount": 500, "currency": "GBP"}'
        secret_key = "abcdef4455"
        signature = "12443c521a6900579d09b1b29cf17b679f7745eb32a8018e46f44bb27103f864"

        result = self.verifier.is_valid(secret_key, signature, payload)

        self.assertFalse(result)

    def test_is_valid_should_return_true_when_signature_is_valid(self):
        payload = '{"amount": 500, "currency": "GBP"}'
        secret_key = "abcdef4455"
        secret_key = "abcdef4455"
        signature = "12443c521a6900579d09b1b29cf17b679f7745eb32a8018e46f44bb27103f865"

        result = self.verifier.is_valid(secret_key, signature, payload)

        self.assertTrue(result)
