# Generated by Django 4.2.11 on 2024-09-25 07:36

import django.contrib.postgres.search
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_post_search_vector'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='search_vector',
            field=django.contrib.postgres.search.SearchVectorField(blank=True, null=True),
        ),
    ]
