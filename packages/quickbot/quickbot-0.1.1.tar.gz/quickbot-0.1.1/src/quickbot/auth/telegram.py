import hashlib
import hmac


def check_telegram_auth(data: dict, bot_token: str) -> bool:
    auth_data = data.copy()
    hash_ = auth_data.pop("hash", None)
    if not hash_:
        return False
    data_check_string = "\n".join([f"{k}={v}" for k, v in sorted(auth_data.items())])
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    hmac_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()
    return hmac_hash == hash_
