# Generated by Django 4.2.6 on 2023-10-31 06:21

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('jwt_authentication', '0013_alter_tokenauthentication_uid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tokenauthentication',
            name='uid',
            field=models.UUIDField(default=uuid.UUID('bc03e5d3-4ea2-4275-a217-295ebd3f5feb')),
        ),
    ]
