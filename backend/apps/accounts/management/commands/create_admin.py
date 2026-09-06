from django.core.management.base import BaseCommand

from apps.accounts.models import AdminUser


class Command(BaseCommand):
    help = "Create initial admin user if none exists"

    def add_arguments(self, parser):
        parser.add_argument("--email", default="admin@shoestore.com")
        parser.add_argument("--password", default="admin123456")
        parser.add_argument("--first-name", default="Store")
        parser.add_argument("--last-name", default="Admin")

    def handle(self, *args, **options):
        if AdminUser.objects.exists():
            self.stdout.write(self.style.WARNING("Admin user already exists."))
            return

        AdminUser.objects.create_superuser(
            email=options["email"],
            password=options["password"],
            first_name=options["first_name"],
            last_name=options["last_name"],
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Created admin: {options['email']} / {options['password']}"
            )
        )
