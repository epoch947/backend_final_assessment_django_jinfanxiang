import os
import csv
import string
import secrets

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings


class Command(BaseCommand):
    help = (
        "Create a single superuser with a random password, "
        "then write its username and password into admin_credentials.csv in the project root."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            type=str,
            default="site_admin",
            help="Username for the new superuser (default: site_admin)",
        )

    def handle(self, *args, **options):
        username = options["username"]
        # If a user with that username already exists and is superuser, skip creation
        if User.objects.filter(username=username, is_superuser=True).exists():
            self.stdout.write(self.style.WARNING(
                f"A superuser named '{username}' already exists; skipping creation."
            ))
            return

        # 1) Generate a random 12-character password
        alphabet = string.ascii_letters + string.digits
        password = "".join(secrets.choice(alphabet) for _ in range(12))

        # 2) Create the superuser
        user = User.objects.create_user(
            username=username,
            email="",
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save()

        # 3) Write username and password into admin_credentials.csv at project root
        base_dir = settings.BASE_DIR
        csv_path = os.path.join(base_dir, "admin_credentials.csv")

        try:
            with open(csv_path, mode="w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["username", "password"])
                writer.writerow([username, password])
            self.stdout.write(self.style.SUCCESS(
                f"Superuser '{username}' created. Credentials written to {csv_path}"
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to write CSV: {e}"))
