from django.core.management.base import BaseCommand

from apps.common.models import StoreSettings


class Command(BaseCommand):
    help = "Initialize store settings singleton"

    def handle(self, *args, **options):
        settings = StoreSettings.load()
        self.stdout.write(
            self.style.SUCCESS(f"Store settings initialized: {settings.business_name}")
        )
