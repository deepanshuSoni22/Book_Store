# Generated by Django 5.2.1 on 2025-05-10 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0004_book_cover_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='file_hash',
            field=models.CharField(blank=True, max_length=64, null=True, unique=True),
        ),
    ]
