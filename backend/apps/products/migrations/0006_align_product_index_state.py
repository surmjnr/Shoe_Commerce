from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("products", "0005_align_configuration_relationship_metadata")]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RenameIndex(
                    model_name="product",
                    old_name="products_pr_categor_14b9c0_idx",
                    new_name="products_pr_categor_9edb3d_idx",
                ),
                migrations.RenameIndex(
                    model_name="product",
                    old_name="products_pr_brand_4bfaa4_idx",
                    new_name="products_pr_brand_i_dc6890_idx",
                ),
            ],
            database_operations=[],
        ),
    ]