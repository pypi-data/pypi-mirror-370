import time


def ttl_cache(ttl: float):
    def decorator(func):
        cache = {}

        def wrapper(*args):
            now = time.time()
            # Remove expired entries
            expired_keys = [k for k, (v, timestamp) in cache.items() if now - timestamp > ttl]
            for k in expired_keys:
                del cache[k]

            # Check the cache
            if args in cache:
                return cache[args][0]

            # Compute the result and cache it
            result = func(*args)
            cache[args] = (result, now)
            return result

        return wrapper

    return decorator
