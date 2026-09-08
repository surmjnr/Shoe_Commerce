from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("products", "0002_productoption")]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="category",
            field=models.CharField(
                choices=[
                    ("SNEAKERS", "Sneakers"),
                    ("RUNNING", "Running"),
                    ("FORMAL", "Formal"),
                    ("CASUAL", "Casual"),
                    ("SANDALS", "Sandals"),
                    ("BOOTS", "Boots"),
                    ("OTHER", "Other"),
                ],
                default="SNEAKERS",
                max_length=100,
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="condition",
            field=models.CharField(
                choices=[
                    ("NEW", "New"),
                    ("LIKE_NEW", "Like New"),
                    ("USED", "Used"),
                ],
                default="NEW",
                max_length=100,
            ),
        ),
    ]