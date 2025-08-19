def get_with_fallback(d, key, fallback_key,default=None):
    return d.get(key, d.get(fallback_key, default))
