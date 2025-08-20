__cache_client__ = None


def create_cache_client():
    """Convenience function to create a redis cache client

    :return: redis client
    """
    from redis import StrictRedis
    from stratus_api.core.settings import get_settings
    global __cache_client__
    if not __cache_client__:
        db_settings = get_settings(settings_type='db')
        __cache_client__ = StrictRedis(host=db_settings['redis_host'], port=int(db_settings['redis_port']),
                                       db=int(db_settings['redis_db']), decode_responses=True)
    return __cache_client__


def cache_data(key, value, expiration_seconds=None):
    import json
    client = create_cache_client()
    client.set(name=key, value=json.dumps(value), ex=expiration_seconds)
    return value


def get_cached_data(key):
    import json
    client = create_cache_client()

    value = client.get(name=key)
    if value is not None:
        value = json.loads(value)
    return value


def delete_cached_keys(keys):
    client = create_cache_client()
    cache_keys = [key for key in keys]
    client.delete(*cache_keys)
    return True
