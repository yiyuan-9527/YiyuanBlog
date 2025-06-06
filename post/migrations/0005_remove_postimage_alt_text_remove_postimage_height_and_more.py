# Generated by Django 5.1.7 on 2025-04-22 08:30

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0004_tagmanagement_post_tags'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='postimage',
            name='alt_text',
        ),
        migrations.RemoveField(
            model_name='postimage',
            name='height',
        ),
        migrations.RemoveField(
            model_name='postimage',
            name='width',
        ),
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.SlugField(allow_unicode=True, unique=True),
        ),
        migrations.AlterField(
            model_name='postimage',
            name='image',
            field=models.ImageField(upload_to='post_images/%Y/%m', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])]),
        ),
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(allow_unicode=True, unique=True),
        ),
    ]
