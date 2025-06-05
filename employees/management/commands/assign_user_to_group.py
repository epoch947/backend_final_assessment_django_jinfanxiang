from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group


class Command(BaseCommand):
    help = "Assign an existing user to a specific group. Usage: python manage.py assign_user_to_group <username> <group_name>"

    def add_arguments(self, parser):
        parser.add_argument(
            "username", type=str, help="The username of the user to assign."
        )
        parser.add_argument(
            "group_name", type=str, help="The name of the group (Admin, HR, Employee)."
        )

    def handle(self, *args, **options):
        username = options["username"]
        group_name = options["group_name"]

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f"User '{username}' does not exist.")

        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            raise CommandError(
                f"Group '{group_name}' does not exist. Run 'create_roles' first."
            )

        # Remove from any other of these three groups
        for g in ["Admin", "HR", "Employee"]:
            if user.groups.filter(name=g).exists():
                user.groups.remove(Group.objects.get(name=g))

        user.groups.add(group)
        user.save()
        self.stdout.write(
            self.style.SUCCESS(f"Added user '{username}' to group '{group_name}'")
        )
