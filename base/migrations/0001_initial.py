# Generated by Django 5.0.6 on 2024-06-20 19:38

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('movie_id', models.IntegerField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('cleaned_title', models.CharField(max_length=255)),
                ('actors', models.TextField(null=True)),
                ('characters', models.TextField(null=True)),
                ('director', models.TextField(null=True)),
                ('writer', models.TextField(null=True)),
                ('composer', models.TextField(null=True)),
                ('composite_string', models.TextField(null=True)),
            ],
        ),
    ]
