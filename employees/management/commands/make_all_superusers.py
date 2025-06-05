from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Make every existing user a superuser (and staff)."

    def handle(self, *args, **options):
        users = User.objects.all()
        total = users.count()
        if total == 0:
            self.stdout.write(self.style.WARNING("No users found."))
            return

        for user in users:
            user.is_superuser = True
            user.is_staff = True
            user.save()
            self.stdout.write(f"Promoted: {user.username} → superuser")

        self.stdout.write(self.style.SUCCESS(f"All {total} users are now superusers."))
