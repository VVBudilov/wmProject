# Generated by Django 5.1.1 on 2024-10-07 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meters', '0004_tariff'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tariff',
            name='tariff_value',
            field=models.DecimalField(decimal_places=2, max_digits=6),
        ),
    ]
