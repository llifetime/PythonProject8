# catalog/views.py
from django.contrib.auth.decorators import login_required
from django.core.checks import messages
from django.views.generic.detail import SingleObjectMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from .models import Product, Category
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache
from django.db.models import Q, Count
import hashlib
import json
import time


# Обновите ProductDetailView для задания 2
class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'
    login_url = reverse_lazy('users:login')

    @method_decorator(cache_page(60 * 15))  # Кешировать страницу на 15 минут
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_object(self, queryset=None):
        """Дополнительное кеширование объекта продукта"""
        cache_key = f'product_detail_{self.kwargs.get("pk")}'

        # Пытаемся получить из кеша
        product = cache.get(cache_key)
        if product is not None:
            print(f"📦 Продукт из кеша: {cache_key}")
            return product

        print(f"🔄 Продукт из БД: {self.kwargs.get('pk')}")
        product = super().get_object(queryset)

        # Увеличиваем счетчик просмотров (не кешируем это)
        product.view_count += 1
        product.save(update_fields=['view_count'])

        # Кешируем на 30 минут
        cache.set(cache_key, product, 60 * 30)

        return product

    def get_context_data(self, **kwargs):
        """Добавление похожих продуктов в контекст"""
        context = super().get_context_data(**kwargs)
        product = self.get_object()

        # Кешируем похожие продукты
        similar_cache_key = f'similar_products_{product.category_id if product.category else "none"}_{product.id}'
        similar_products = cache.get(similar_cache_key)

        if similar_products is None:
            similar_products = Product.objects.filter(
                category=product.category,
                publish_status='published'
            ).exclude(id=product.id).select_related('owner', 'category')[:4]
            cache.set(similar_cache_key, similar_products, 60 * 30)

        context['similar_products'] = similar_products
        return context


# Обновите ProductListView для задания 4
class ProductListView(ListView):
    model = Product
    template_name = 'catalog/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    @method_decorator(cache_page(60 * 5))  # Кешировать страницу на 5 минут
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        """Получение QuerySet с низкоуровневым кешированием"""
        # Генерация ключа кеша на основе параметров запроса
        cache_key = self._generate_cache_key()

        # Пытаемся получить из кеша
        start_time = time.time()
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            print(f"📦 Список продуктов из кеша: {cache_key} ({time.time() - start_time:.3f} сек)")
            return cached_data

        print(f"🔄 Список продуктов из БД: {cache_key}")
        queryset = self._get_filtered_queryset()

        # Оптимизация запросов
        optimized_queryset = queryset.select_related(
            'owner', 'category'
        ).prefetch_related('images').order_by('-created_at')

        # Кешируем на 10 минут
        cache.set(cache_key, optimized_queryset, 60 * 10)

        return optimized_queryset

    def _generate_cache_key(self):
        """Генерация ключа кеша на основе параметров запроса"""
        params = {
            'search': self.request.GET.get('search', ''),
            'category': self.request.GET.get('category', ''),
            'sort': self.request.GET.get('sort', '-created_at'),
            'page': self.request.GET.get('page', 1),
            'user_id': self.request.user.id if self.request.user.is_authenticated else 'anonymous',
        }

        # Создаем хэш из параметров
        param_string = json.dumps(params, sort_keys=True)
        hash_key = hashlib.md5(param_string.encode()).hexdigest()

        return f'product_list:{hash_key}'

    def _get_filtered_queryset(self):
        """Фильтрация QuerySet на основе параметров запроса"""
        queryset = Product.objects.filter(publish_status='published')

        # Поиск
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        # Категория
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)

        # Сортировка
        sort = self.request.GET.get('sort', '-created_at')
        if sort in ['name', '-name', 'price', '-price', '-created_at']:
            queryset = queryset.order_by(sort)

        return queryset

    def get_context_data(self, **kwargs):
        """Добавление кешированных данных в контекст"""
        context = super().get_context_data(**kwargs)

        # Кешируем категории для фильтра
        categories_cache_key = 'all_categories_for_filter'
        categories = cache.get(categories_cache_key)

        if categories is None:
            categories = Category.objects.annotate(
                product_count=Count('product', filter=Q(product__publish_status='published'))
            ).filter(product_count__gt=0)
            cache.set(categories_cache_key, categories, 60 * 60)  # 1 час

        context['categories'] = categories
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_category'] = self.request.GET.get('category', '')

        # Статистика продуктов (кешированная)
        stats_cache_key = 'product_stats_global'
        stats = cache.get(stats_cache_key)

        if stats is None:
            from django.db.models import Avg
            stats = Product.objects.filter(
                publish_status='published'
            ).aggregate(
                total_products=Count('id'),
                avg_price=Avg('price'),
            )
            cache.set(stats_cache_key, stats, 60 * 30)  # 30 минут

        context['stats'] = stats

        return context


# Добавьте новое представление для задания 3
from .services import ProductCacheService, get_cached_products_by_category


class CategoryProductsView(ListView):
    """
    Представление для отображения продуктов по категории
    Использует сервисные функции с кешированием
    """
    template_name = 'catalog/category_products.html'
    context_object_name = 'products'
    paginate_by = 12

    @method_decorator(cache_page(60 * 10))  # Кешировать на 10 минут
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        """Получение продуктов через сервис с кешированием"""
        category_slug = self.kwargs.get('category_slug')
        return get_cached_products_by_category(category_slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs.get('category_slug')

        # Получаем статистику категории
        from .services import get_cached_category_stats
        stats = get_cached_category_stats(category_slug)

        # Получаем объект категории
        try:
            category = Category.objects.get(slug=category_slug)
            context['category'] = category
        except Category.DoesNotExist:
            context['category'] = None

        context['stats'] = stats
        context['category_slug'] = category_slug

        return context