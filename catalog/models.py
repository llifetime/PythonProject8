from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class Category(models.Model):
    name = models.CharField(_('название'), max_length=100)
    description = models.TextField(_('описание'), blank=True)

    class Meta:
        verbose_name = _('категория')
        verbose_name_plural = _('категории')

    def __str__(self):
        return self.name


class Product(models.Model):
    # Существующие поля
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

    # НОВЫЕ ПОЛЯ ДЛЯ ЗАДАНИЯ 1 И 2
    PUBLISH_STATUS_CHOICES = [
        ('draft', _('Черновик')),
        ('published', _('Опубликовано')),
        ('unpublished', _('Снято с публикации')),
    ]

    publish_status = models.CharField(
        _('статус публикации'),
        max_length=20,
        choices=PUBLISH_STATUS_CHOICES,
        default='draft'
    )

    # Поле владельца для задания 2
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('владелец'),
        related_name='products',
        null=True,  # Для совместимости с существующими данными
        blank=True
    )

    class Meta:
        verbose_name = _('товар')
        verbose_name_plural = _('товары')
        ordering = ['-created_at']
        permissions = [
            ("can_unpublish_product", _("Может снимать товары с публикации")),
            ("can_change_publish_status", _("Может изменять статус публикации")),
        ]

    def __str__(self):
        return self.name

    def is_owner(self, user):
        """Проверяет, является ли пользователь владельцем товара"""
        return self.owner == user

    def can_be_edited_by(self, user):
        """Проверяет, может ли пользователь редактировать товар"""
        return self.owner == user

    def can_be_deleted_by(self, user):
        return (
                self.owner == user or
                user.has_perm('catalog.delete_product')  # ✅ Исправленное приложение
        )


# ДЛЯ ДОПОЛНИТЕЛЬНОГО ЗАДАНИЯ (если нужно)
class BlogPost(models.Model):
    title = models.CharField(_('заголовок'), max_length=200)
    content = models.TextField(_('содержание'))
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('автор'),
        related_name='blog_posts'
    )
    is_published = models.BooleanField(_('опубликовано'), default=False)
    created_at = models.DateTimeField(_('дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('дата обновления'), auto_now=True)

    class Meta:
        verbose_name = _('запись блога')
        verbose_name_plural = _('записи блога')
        ordering = ['-created_at']
        permissions = [
            ("manage_blog_posts", _("Может управлять записями блога")),
        ]

    def __str__(self):
        return self.title