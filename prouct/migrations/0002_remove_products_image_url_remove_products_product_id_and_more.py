# Recreated to match already-applied migration recorded in django_migrations.
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prouct', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='products',
            name='image_url',
        ),
        migrations.RemoveField(
            model_name='products',
            name='product_id',
        ),
        migrations.AddField(
            model_name='products',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AddField(
            model_name='products',
            name='image',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
