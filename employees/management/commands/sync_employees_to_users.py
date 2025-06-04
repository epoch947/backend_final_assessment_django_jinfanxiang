
import random
import string
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from employees.models import Employee


class Command(BaseCommand):
    help = (
        "For each Employee without a linked User, create a new User whose "
        "username matches Employee.name. Then link Employee.user → that User. "
        "If a User already exists but the username differs, update it to match Employee.name."
    )

    def handle(self, *args, **options):
        # Loop through all Employee records
        all_emps = Employee.objects.all()
        count_created = 0
        count_updated = 0

        for emp in all_emps:
            # Desired username is exactly the employee's name (including spaces)
            desired_username = emp.name.strip()

            if emp.user_id:
                # This Employee already has a linked User; check if username needs correction
                user = emp.user
                if user.username != desired_username:
                    old_username = user.username
                    # But first ensure no other User has this desired_username.
                    # If there is a conflict, append a number suffix until unique.
                    base = desired_username
                    new_username = base
                    suffix = 1
                    while User.objects.exclude(pk=user.pk).filter(username=new_username).exists():
                        new_username = f"{base}_{suffix}"
                        suffix += 1

                    user.username = new_username
                    user.save()
                    count_updated += 1
                    self.stdout.write(
                        f"Updated User(id={user.pk}) username '{old_username}' → '{new_username}' "
                        f"for Employee(id={emp.pk}, name='{emp.name}')"
                    )
                else:
                    # Already in sync, nothing to do
                    continue

            else:
                # No linked User yet → create one with username = Employee.name
                # First ensure that no other User already has exactly that username
                base = desired_username
                new_username = base
                suffix = 1
                while User.objects.filter(username=new_username).exists():
                    new_username = f"{base}_{suffix}"
                    suffix += 1

                # Create a random password (we can randomize it again later)
                random_password = "".join(
                    random.choices(string.ascii_letters + string.digits, k=12)
                )
                user = User.objects.create_user(
                    username=new_username,
                    email=emp.email,
                    password=random_password
                )
                # Mark the user active and staff (so they can log into /admin/)
                user.is_active = True
                user.is_staff = True
                user.save()

                # Link the Employee record to this newly created user
                emp.user = user
                emp.save()

                count_created += 1
                self.stdout.write(
                    f"Created User(id={user.pk}, username='{new_username}') for "
                    f"Employee(id={emp.pk}, name='{emp.name}'). "
                    f"Temporary password: {random_password}"
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Finished syncing. Users created: {count_created}, Users updated: {count_updated}."
            )
        )
