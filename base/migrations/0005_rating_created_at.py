# Generated by Django 5.0.6 on 2024-07-15 16:15

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_alter_rating_rating_review'),
    ]

    operations = [
        migrations.AddField(
            model_name='rating',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
