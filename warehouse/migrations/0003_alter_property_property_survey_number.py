# Generated by Django 4.1.4 on 2023-02-21 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0002_alter_gala_gala_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='property_survey_number',
            field=models.CharField(max_length=36, unique=True),
        ),
    ]
