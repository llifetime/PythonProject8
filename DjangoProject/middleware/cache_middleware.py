# middleware/cache_middleware.py
from django.core.cache import cache
import hashlib
import json


class CacheResponseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Кешируем только GET запросы для API
        if request.method == 'GET' and request.path.startswith('/api/'):
            cache_key = self._generate_cache_key(request)
            cached_response = cache.get(cache_key)

            if cached_response:
                return cached_response

        response = self.get_response(request)

        # Кешируем успешные GET ответы API
        if (request.method == 'GET' and
                request.path.startswith('/api/') and
                response.status_code == 200):
            cache_key = self._generate_cache_key(request)
            cache.set(cache_key, response, 60 * 5)  # 5 минут

        return response

    def _generate_cache_key(self, request):
        """Генерация ключа кеша на основе запроса"""
        key_data = {
            'path': request.path,
            'query': request.GET.urlencode(),
            'user_id': request.user.id if request.user.is_authenticated else 'anonymous',
        }

        key_string = json.dumps(key_data, sort_keys=True)
        return f"api_cache_{hashlib.md5(key_string.encode()).hexdigest()}"