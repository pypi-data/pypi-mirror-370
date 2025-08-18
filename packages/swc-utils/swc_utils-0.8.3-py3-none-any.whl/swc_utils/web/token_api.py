from swc_utils.redis_db import get_app_redis_interface


def get_app_stack_crypto_key():
    return get_app_redis_interface().event_manager.query("get-app-stack-crypto-key")
