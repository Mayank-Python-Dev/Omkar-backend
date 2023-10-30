# Generated by Django 4.1.4 on 2023-07-13 07:37

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contract', '0003_remove_rental_locking_period_contracthistory'),
    ]

    operations = [
        migrations.AddField(
            model_name='rental',
            name='locking_period',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.DeleteModel(
            name='ContractHistory',
        ),
    ]