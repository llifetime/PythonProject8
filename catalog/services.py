# catalog/services.py
from django.core.cache import cache
from django.db.models import Prefetch, Q, Count, Avg, Sum
from .models import Product, Category
import hashlib
import json
import time


class ProductCacheService:
    """Сервис для кеширования операций с продуктами"""

    @staticmethod
    def generate_cache_key(prefix, **params):
        """Генерация уникального ключа кеша на основе параметров"""
        sorted_params = json.dumps(params, sort_keys=True)
        hash_key = hashlib.md5(sorted_params.encode()).hexdigest()
        return f"{prefix}:{hash_key}"

    @staticmethod
    def get_products_by_category(category_slug, include_unpublished=False, limit=None):
        """
        Получение продуктов по категории с кешированием

        Args:
            category_slug: slug категории
            include_unpublished: включать неопубликованные товары (только для админов)
            limit: ограничение количества

        Returns:
            Список продуктов
        """
        # Генерация ключа кеша
        cache_key = ProductCacheService.generate_cache_key(
            'products_by_category',
            category_slug=category_slug,
            include_unpublished=include_unpublished,
            limit=limit
        )

        # Пытаемся получить из кеша
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            print(f"📦 Данные из кеша: {cache_key}")
            return cached_data

        print(f"🔄 Получаем из БД: {category_slug}")

        try:
            # Получаем категорию
            category = Category.objects.get(slug=category_slug)
        except Category.DoesNotExist:
            return []

        # Формируем запрос
        queryset = Product.objects.filter(category=category)

        if not include_unpublished:
            queryset = queryset.filter(publish_status='published')

        # Оптимизация запросов
        queryset = queryset.select_related('owner', 'category').prefetch_related(
            Prefetch('images')
        ).order_by('-created_at')

        if limit:
            queryset = queryset[:limit]

        result = list(queryset)

        # Кешируем на 10 минут
        cache.set(cache_key, result, 60 * 10)

        return result

    @staticmethod
    def get_category_stats(category_slug):
        """
        Получение статистики по категории с кешированием

        Returns:
            Словарь со статистикой
        """
        cache_key = f'category_stats:{category_slug}'

        # Пробуем получить из кеша
        stats = cache.get(cache_key)
        if stats is not None:
            return stats

        try:
            category = Category.objects.get(slug=category_slug)

            # Получаем продукты категории
            products = Product.objects.filter(
                category=category,
                publish_status='published'
            )

            # Вычисляем статистику
            from django.db.models import Max, Min
            stats = products.aggregate(
                total_products=Count('id'),
                avg_price=Avg('price'),
                max_price=Max('price'),
                min_price=Min('price'),
                total_views=Sum('view_count'),
            )

            # Добавляем информацию о категории
            stats.update({
                'category_name': category.name,
                'category_description': category.description or '',
                'category_slug': category.slug,
            })

            # Кешируем на 30 минут
            cache.set(cache_key, stats, 60 * 30)

            return stats

        except Category.DoesNotExist:
            return {}

    @staticmethod
    def get_featured_products(limit=8):
        """Получение рекомендуемых продуктов с кешированием"""
        cache_key = f'featured_products:{limit}'

        products = cache.get(cache_key)
        if products is not None:
            return products

        products = list(Product.objects.filter(
            is_featured=True,
            publish_status='published'
        ).select_related('category', 'owner')[:limit])

        cache.set(cache_key, products, 60 * 60)  # 1 час

        return products

    @staticmethod
    def invalidate_category_cache(category_slug):
        """Инвалидация кеша категории"""
        # Удаляем все ключи, связанные с категорией
        cache.delete(f'category_stats:{category_slug}')

        # Удаляем кеш продуктов категории (по шаблону)
        # В production нужно использовать redis.scan
        cache.delete_pattern(f'products_by_category:*{category_slug}*')


# Упрощенный интерфейс для быстрого использования
def get_cached_products_by_category(category_slug, **kwargs):
    """Упрощенная функция для получения продуктов по категории"""
    return ProductCacheService.get_products_by_category(category_slug, **kwargs)


def get_cached_category_stats(category_slug):
    """Упрощенная функция для получения статистики категории"""
    return ProductCacheService.get_category_stats(category_slug)