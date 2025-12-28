from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = 'Create Moderator Products group'

    def handle(self, *args, **options):
        moderator_group, created = Group.objects.get_or_create(name='Модераторы продуктов')

        if not created:
            self.stdout.write('Группа Модераторов продуктов уже существует.')
        else:
            can_unpublish_permission = Permission.objects.get(codename='can_unpublish_product')
            delete_product_permission = Permission.objects.get(codename='delete_product')

            moderator_group.permissions.set([can_unpublish_permission, delete_product_permission])
            self.stdout.write('Группа Модераторов продуктов создана успешно!')