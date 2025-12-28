# catalog/views.py
from django.views.generic.detail import SingleObjectMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Product
from .forms import ProductForm
from django.shortcuts import redirect
from django.http import HttpResponseForbidden, HttpResponse


class UnpublishProductView(SingleObjectMixin, RedirectView):
    model = Product
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        product = self.get_object()
        if request.user.has_perm('catalog.can_unpublish_product'):  # Исправленное пространство имён
            product.published = False
            product.save()
            return redirect(reverse_lazy('catalog:product_list'))
        else:
            return HttpResponseForbidden("Вы не имеете достаточных прав.")

    def get_queryset(self):
        return Product.objects.all()

class ProductListView(ListView):
    model = Product
    template_name = 'catalog/product_list.html'
    context_object_name = 'products'

# ДОЛЖНО БЫТЬ:
class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'
    login_url = reverse_lazy('users:login')

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy('catalog:product_list')
    login_url = reverse_lazy('users:login')

    def form_valid(self, form):
        """
        Перед сохранением объекта автоматически устанавливаем текущего пользователя как владельца.
        """
        obj = form.save(commit=False)
        obj.owner = self.request.user  # Текущий пользователь назначается владельцем
        obj.save()
        return super().form_valid(form)

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy('catalog:product_list')
    login_url = reverse_lazy('users:login')

    def dispatch(self, request, *args, **kwargs):
        """
        Проверяем, может ли текущий пользователь редактировать продукт.
        Доступ открыт только владельцу продукта или пользователям с полномочиями.
        """
        product = self.get_object()
        if product.owner != self.request.user and not self.request.user.has_perm('catalog.change_product'):
            return HttpResponseForbidden("Вы не можете редактировать этот продукт.")
        return super().dispatch(request, *args, **kwargs)

class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'catalog/product_confirm_delete.html'
    success_url = reverse_lazy('catalog:product_list')
    login_url = reverse_lazy('users:login')

    def dispatch(self, request, *args, **kwargs):
        """
        Проверяем, может ли текущий пользователь удалить продукт.
        Доступ открыт только владельцу продукта или пользователям с полномочиями.
        """
        product = self.get_object()
        if product.owner != self.request.user and not self.request.user.has_perm('catalog.delete_product'):
            return HttpResponseForbidden("Вы не можете удалить этот продукт.")
        return super().dispatch(request, *args, **kwargs)