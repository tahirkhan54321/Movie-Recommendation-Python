# Generated by Django 5.0.6 on 2024-09-05 15:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_watchlist'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='budget',
            field=models.BigIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='revenue',
            field=models.BigIntegerField(null=True),
        ),
    ]
