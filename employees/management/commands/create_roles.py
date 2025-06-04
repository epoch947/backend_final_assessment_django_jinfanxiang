

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = "Create Admin, HR, and Employee groups (if they do not yet exist)."

    def handle(self, *args, **options):
        roles = ["Admin", "HR", "Employee"]
        for role_name in roles:
            group, created = Group.objects.get_or_create(name=role_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created group '{role_name}'"))
            else:
                self.stdout.write(f"Group '{role_name}' already exists")
