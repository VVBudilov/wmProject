# Generated by Django 5.1.1 on 2024-10-09 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meters', '0006_house_house_ind_house_house_odn'),
    ]

    operations = [
        migrations.AddField(
            model_name='house',
            name='house_status',
            field=models.CharField(default='', max_length=255),
        ),
    ]
