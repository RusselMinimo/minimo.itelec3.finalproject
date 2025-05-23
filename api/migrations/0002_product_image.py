# Generated by Django 5.0.2 on 2025-05-18 09:58

import authentication.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='product_images', validators=[authentication.models.validate_image_size, authentication.models.validate_image_type]),
        ),
    ]
