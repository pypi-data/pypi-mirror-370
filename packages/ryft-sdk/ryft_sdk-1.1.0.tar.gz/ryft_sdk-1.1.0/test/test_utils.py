import unittest
from ryft_sdk.utils import determine_base_url


class TestUtils(unittest.TestCase):
    def test_determine_base_url_with_live_key(self):
        url = determine_base_url("sk_live_example123")
        self.assertEqual(url, "https://api.ryftpay.com/v1")

    def test_determine_base_url_with_test_key(self):
        url = determine_base_url("sk_sandbox_example123")
        self.assertEqual(url, "https://sandbox-api.ryftpay.com/v1")

    def test_determine_base_url_with_other_key(self):
        url = determine_base_url("some_other_key")
        self.assertEqual(url, "https://sandbox-api.ryftpay.com/v1")


if __name__ == "__main__":
    unittest.main()
