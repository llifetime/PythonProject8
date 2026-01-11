# utils/redis_monitoring.py
import redis
from django.conf import settings


def get_redis_stats():
    """Получение статистики Redis"""
    try:
        r = redis.Redis.from_url(settings.CACHES['default']['LOCATION'])

        info = r.info()

        stats = {
            'connected': True,
            'used_memory': info['used_memory_human'],
            'total_keys': info['db1']['keys'] if 'db1' in info else 0,
            'hits': info['keyspace_hits'],
            'misses': info['keyspace_misses'],
            'hit_rate': info['keyspace_hits'] / (info['keyspace_hits'] + info['keyspace_misses'])
            if (info['keyspace_hits'] + info['keyspace_misses']) > 0 else 0,
        }

        return stats
    except Exception as e:
        return {'connected': False, 'error': str(e)}