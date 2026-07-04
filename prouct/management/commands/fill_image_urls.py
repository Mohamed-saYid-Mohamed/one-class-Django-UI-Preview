from django.core.management.base import BaseCommand

from prouct.models import products


class Command(BaseCommand):
    help = "Fill empty image_url values for all products with deterministic placeholder URLs."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Overwrite existing image_url values too.",
        )

    def handle(self, *args, **options):
        force = options["force"]
        updated_count = 0

        for product in products.objects.all():
            if force or self._is_empty(product.image_url):
                product.image_url = [
                    f"https://picsum.photos/seed/product-{product.product_id}/600/400"
                ]
                product.save(update_fields=["image_url"])
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Updated {updated_count} product(s). Use --force to overwrite all."
            )
        )

    @staticmethod
    def _is_empty(value):
        if value is None:
            return True

        if isinstance(value, list):
            cleaned = [str(item).strip() for item in value if str(item).strip()]
            return len(cleaned) == 0

        if isinstance(value, str):
            return value.strip() in {"", "[]", "null", "None"}

        return False
