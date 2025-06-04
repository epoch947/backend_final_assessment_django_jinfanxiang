
import csv
import os
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group

class Command(BaseCommand):
    help = "Bulk assign users to groups from a CSV file."

    def add_arguments(self, parser):
        parser.add_argument(
            'mapping_file',
            type=str,
            help="Path to CSV file containing 'username,group_name' per line."
        )

    def handle(self, *args, **options):
        file_path = options['mapping_file']

        # Ensure the file exists
        if not os.path.exists(file_path):
            raise CommandError(f"File not found: {file_path}")

        with open(file_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            line_count = 0

            for row in reader:
                line_count += 1
                if len(row) < 2:
                    self.stdout.write(self.style.WARNING(
                        f"Line {line_count}: Expected 2 columns, got {len(row)}. Skipping."
                    ))
                    continue

                username = row[0].strip()
                group_name = row[1].strip()

                # Lookup the user
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    self.stdout.write(self.style.WARNING(
                        f"Line {line_count}: no such user '{username}'. Skipping."
                    ))
                    continue

                # Lookup the group
                try:
                    group = Group.objects.get(name=group_name)
                except Group.DoesNotExist:
                    self.stdout.write(self.style.WARNING(
                        f"Line {line_count}: no such group '{group_name}'. Skipping."
                    ))
                    continue

                # Remove from all three roles first
                for gname in ["Admin", "HR", "Employee"]:
                    g = Group.objects.filter(name=gname).first()
                    if g and user.groups.filter(name=gname).exists():
                        user.groups.remove(g)

                # Add to correct group
                user.groups.add(group)
                user.save()
                self.stdout.write(self.style.SUCCESS(
                    f"Line {line_count}: Assigned user '{username}' → group '{group_name}'"
                ))

            self.stdout.write(self.style.SUCCESS("Bulk group assignment completed."))
