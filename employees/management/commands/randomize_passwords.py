import string
import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from employees.models import Employee


class Command(BaseCommand):
    help = (
        "Generate a random password for each existing User (linked via Employee), "
        "ensure username == Employee.name, mark each user as staff, "
        "and print out 'Employee.name,new_password'."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--length',
            type=int,
            default=12,
            help="Length of the randomly generated password (default: 12)",
        )
        parser.add_argument(
            '--make-superuser',
            action='store_true',
            help="If provided, set is_superuser=True on every user as well.",
        )

    def handle(self, *args, **options):
        length = options['length']
        make_super = options['make_superuser']

        def generate_password(length):
            alphabet = string.ascii_letters + string.digits
            return "".join(random.choice(alphabet) for _ in range(length))

        # Loop over all Employee objects (tie each User back to Employee.name)
        all_emps = Employee.objects.select_related('user').all()
        total = all_emps.count()

        if total == 0:
            self.stdout.write(self.style.WARNING("No employees (and hence no users) found."))
            return

        self.stdout.write(self.style.NOTICE(f"Randomizing passwords for {total} users (by Employee.name)..."))

        for emp in all_emps:
            user = emp.user
            if not user:
                # Shouldn't happen if sync_employees_to_users was run; skip if no linked user.
                self.stdout.write(self.style.WARNING(
                    f"Employee(id={emp.pk}, name='{emp.name}') has no linked User. Skipping."
                ))
                continue

            new_pwd = generate_password(length)
            user.set_password(new_pwd)
            user.is_active = True
            user.is_staff = True
            if make_super:
                user.is_superuser = True
            user.save()

            # Print "Employee.name,new_password"
            self.stdout.write(f"{emp.name},{new_pwd}")

        self.stdout.write(self.style.SUCCESS(f"Completed randomization for {total} users."))
