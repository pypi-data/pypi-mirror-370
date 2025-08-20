from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Automatically creates a superuser for the demo app"

    def add_arguments(self, parser):
        parser.add_argument("--username", type=str, default="admin", help="Username for the superuser (default: admin)")
        parser.add_argument(
            "--email",
            type=str,
            default="admin@example.com",
            help="Email for the superuser (default: admin@example.com)",
        )
        parser.add_argument(
            "--password", type=str, default="admin123", help="Password for the superuser (default: admin123)"
        )

    def handle(self, *args, **options):
        username = options["username"]
        email = options["email"]
        password = options["password"]

        # Check if superuser already exists
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(self.style.WARNING("A superuser already exists. Skipping creation."))
            return

        # Create superuser
        try:
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Successfully created superuser "{username}" with email "{email}"'))
            self.stdout.write(self.style.SUCCESS("You can now log in to the admin interface at /admin/"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to create superuser: {e}"))
