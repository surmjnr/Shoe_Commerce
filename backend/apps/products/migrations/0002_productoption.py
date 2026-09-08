from django.db import migrations, models


def seed_product_options(apps, schema_editor):
    ProductOption = apps.get_model("products", "ProductOption")
    defaults = {
        "BRAND": [("Nike", "Nike"), ("Adidas", "Adidas"), ("Puma", "Puma")],
        "CATEGORY": [("SNEAKERS", "Sneakers"), ("RUNNING", "Running"), ("FORMAL", "Formal"), ("CASUAL", "Casual"), ("SANDALS", "Sandals"), ("BOOTS", "Boots"), ("OTHER", "Other")],
        "CONDITION": [("NEW", "New"), ("LIKE_NEW", "Like New"), ("USED", "Used")],
        "COLOR": [("Black", "Black"), ("White", "White"), ("Red", "Red"), ("Blue", "Blue"), ("Brown", "Brown")],
        "SIZE": [(str(size), str(size)) for size in range(36, 46)],
    }
    for option_type, options in defaults.items():
        ProductOption.objects.bulk_create([
            ProductOption(option_type=option_type, value=value, label=label)
            for value, label in options
        ])


class Migration(migrations.Migration):
    dependencies = [("products", "0001_initial")]
    operations = [
        migrations.CreateModel(
            name="ProductOption",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("option_type", models.CharField(choices=[("BRAND", "Brand"), ("CATEGORY", "Category"), ("CONDITION", "Condition"), ("COLOR", "Color"), ("SIZE", "Size")], max_length=20)),
                ("value", models.CharField(max_length=100)),
                ("label", models.CharField(max_length=100)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["option_type", "label"]},
        ),
        migrations.AddConstraint(
            model_name="productoption",
            constraint=models.UniqueConstraint(fields=("option_type", "value"), name="unique_product_option_value"),
        ),
        migrations.RunPython(seed_product_options, migrations.RunPython.noop),
    ]