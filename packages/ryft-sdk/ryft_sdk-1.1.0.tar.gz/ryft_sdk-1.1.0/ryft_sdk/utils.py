def determine_base_url(secret_key: str) -> str:
    """
    Determine the base URL based on the secret key pattern.

    Args:
        secret_key: The Ryft API secret key

    Returns:
        The appropriate base URL for the API
    """
    if secret_key.startswith("sk_live_"):
        return "https://api.ryftpay.com/v1"
    else:
        return "https://sandbox-api.ryftpay.com/v1"
