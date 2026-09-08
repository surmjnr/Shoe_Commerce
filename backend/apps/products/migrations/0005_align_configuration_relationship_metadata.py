import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("products", "0004_product_configuration_models")]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="brand",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="products", to="products.brand"),
        ),
        migrations.AlterField(
            model_name="product",
            name="category",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="products", to="products.category"),
        ),
        migrations.AlterField(
            model_name="product",
            name="condition",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="products", to="products.condition"),
        ),
        migrations.AlterField(
            model_name="product",
            name="color",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="products", to="products.color"),
        ),
        migrations.AlterField(
            model_name="productvariant",
            name="size",
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name="variants", to="products.size"),
        ),
    ]