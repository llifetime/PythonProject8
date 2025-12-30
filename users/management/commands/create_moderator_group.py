from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from catalog.models import Product


class Command(BaseCommand):
    help = 'Create Moderator Products group'

    def handle(self, *args, **options):
        # Корректируем название группы
        moderator_group, created = Group.objects.get_or_create(name='Модератор продуктов')

        if not created:
            self.stdout.write('Группа Модератора продуктов уже существует.')
        else:
            # Получаем тип контента для модели Product
            product_content_type = ContentType.objects.get_for_model(Product)

            # Получаем права доступа по типу контента и codename
            can_unpublish_permission = Permission.objects.get(codename='can_unpublish_product',
                                                              content_type=product_content_type)
            delete_product_permission = Permission.objects.get(codename='delete_product',
                                                               content_type=product_content_type)

            # Назначаем разрешения группе
            moderator_group.permissions.set([can_unpublish_permission, delete_product_permission])
            self.stdout.write('Группа Модератора продуктов создана успешно!')