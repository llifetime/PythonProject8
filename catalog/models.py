from django.db import models
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    name = models.CharField(_('название'), max_length=100)
    description = models.TextField(_('описание'), blank=True)

    class Meta:
        verbose_name = _('категория')
        verbose_name_plural = _('категории')

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(_('название'), max_length=200)
    description = models.TextField(_('описание'))
    price = models.DecimalField(_('цена'), max_digits=10, decimal_places=2)
    image = models.ImageField(
        _('изображение'),
        upload_to='products/',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(_('дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('дата обновления'), auto_now=True)

    # ИСПРАВЛЕННАЯ СТРОКА (согласно описанию проблемы)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name='Категория',
        related_name='products'
    )

    class Meta:
        verbose_name = _('товар')
        verbose_name_plural = _('товары')
        ordering = ['-created_at']

    def __str__(self):
        return self.name