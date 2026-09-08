from django.db import migrations, models
import django.db.models.deletion


DEFAULTS = {
    "brand": [("Nike", "Nike"), ("Adidas", "Adidas"), ("Puma", "Puma")],
    "category": [("SNEAKERS", "Sneakers"), ("RUNNING", "Running"), ("FORMAL", "Formal"), ("CASUAL", "Casual"), ("SANDALS", "Sandals"), ("BOOTS", "Boots"), ("OTHER", "Other")],
    "condition": [("NEW", "New"), ("LIKE_NEW", "Like New"), ("USED", "Used")],
    "color": [("Black", "Black"), ("White", "White"), ("Red", "Red"), ("Blue", "Blue"), ("Brown", "Brown")],
    "size": [(str(value), str(value)) for value in range(36, 46)],
}


def seed_and_map_configuration(apps, schema_editor):
    Brand = apps.get_model("products", "Brand")
    Category = apps.get_model("products", "Category")
    Condition = apps.get_model("products", "Condition")
    Color = apps.get_model("products", "Color")
    Size = apps.get_model("products", "Size")
    Product = apps.get_model("products", "Product")
    ProductVariant = apps.get_model("products", "ProductVariant")
    ProductOption = apps.get_model("products", "ProductOption")

    model_map = {"BRAND": Brand, "CATEGORY": Category, "CONDITION": Condition, "COLOR": Color, "SIZE": Size}
    values = {key: {} for key in DEFAULTS}
    for option_type, model in model_map.items():
        field_name = option_type.lower()
        for option in ProductOption.objects.filter(option_type=option_type):
            raw_value = option.value.strip()
            if not raw_value:
                continue
            if field_name in ("category", "condition"):
                lookup = {"value__iexact": raw_value}
                obj, _ = model.objects.get_or_create(value=raw_value, defaults={"name": option.label.strip() or raw_value})
                if obj.name != (option.label.strip() or raw_value):
                    obj.name = option.label.strip() or raw_value
                    obj.save(update_fields=["name"])
            elif field_name == "size":
                obj, _ = model.objects.get_or_create(value=raw_value)
            else:
                obj, _ = model.objects.get_or_create(name=raw_value)
            values[field_name][raw_value.casefold()] = obj

        for raw_value, label in DEFAULTS[field_name]:
            if field_name in ("category", "condition"):
                obj, _ = model.objects.get_or_create(value=raw_value, defaults={"name": label})
            elif field_name == "size":
                obj, _ = model.objects.get_or_create(value=raw_value)
            else:
                obj, _ = model.objects.get_or_create(name=raw_value)
            values[field_name][raw_value.casefold()] = obj

    for product in Product.objects.all():
        updates = {}
        for field_name, model in (("brand", Brand), ("category", Category), ("condition", Condition), ("color", Color)):
            raw_value = getattr(product, field_name)
            if not raw_value:
                continue
            option = values[field_name].get(raw_value.strip().casefold())
            if not option:
                if field_name in ("category", "condition"):
                    option, _ = model.objects.get_or_create(value=raw_value.strip(), defaults={"name": raw_value.strip().replace("_", " ").title()})
                else:
                    option, _ = model.objects.get_or_create(name=raw_value.strip())
                values[field_name][raw_value.strip().casefold()] = option
            updates[f"{field_name}_ref_id"] = option.pk
        if updates:
            Product.objects.filter(pk=product.pk).update(**updates)

    for variant in ProductVariant.objects.all():
        raw_value = variant.size
        option = values["size"].get(raw_value.strip().casefold())
        if not option:
            option, _ = Size.objects.get_or_create(value=raw_value.strip())
            values["size"][raw_value.strip().casefold()] = option
        ProductVariant.objects.filter(pk=variant.pk).update(size_ref_id=option.pk)


class Migration(migrations.Migration):
    dependencies = [("products", "0003_widen_product_option_fields")]

    operations = [
        migrations.CreateModel(
            name="Brand",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=100, unique=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("value", models.CharField(max_length=100, unique=True)),
                ("name", models.CharField(max_length=100)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Condition",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("value", models.CharField(max_length=100, unique=True)),
                ("name", models.CharField(max_length=100)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Color",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=100, unique=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Size",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("value", models.CharField(max_length=20, unique=True)),
            ],
            options={"ordering": ["value"]},
        ),
        migrations.AddField(model_name="product", name="brand_ref", field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="products_new", to="products.brand")),
        migrations.AddField(model_name="product", name="category_ref", field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="products_new", to="products.category")),
        migrations.AddField(model_name="product", name="condition_ref", field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="products_new", to="products.condition")),
        migrations.AddField(model_name="product", name="color_ref", field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="products_new", to="products.color")),
        migrations.AddField(model_name="productvariant", name="size_ref", field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name="variants_new", to="products.size")),
        migrations.RunPython(seed_and_map_configuration, migrations.RunPython.noop),
        migrations.RemoveField(model_name="product", name="brand"),
        migrations.RemoveField(model_name="product", name="category"),
        migrations.RemoveField(model_name="product", name="condition"),
        migrations.RemoveField(model_name="product", name="color"),
        migrations.RemoveField(model_name="productvariant", name="size"),
        migrations.RenameField(model_name="product", old_name="brand_ref", new_name="brand"),
        migrations.RenameField(model_name="product", old_name="category_ref", new_name="category"),
        migrations.RenameField(model_name="product", old_name="condition_ref", new_name="condition"),
        migrations.RenameField(model_name="product", old_name="color_ref", new_name="color"),
        migrations.RenameField(model_name="productvariant", old_name="size_ref", new_name="size"),
        migrations.AlterUniqueTogether(name="productvariant", unique_together={("product", "size")}),
        migrations.DeleteModel(name="ProductOption"),
    ]