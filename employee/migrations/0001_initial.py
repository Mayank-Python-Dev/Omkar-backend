# Generated by Django 4.1.4 on 2023-01-30 07:23

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.UUIDField(blank=True, default=uuid.uuid4, editable=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=50)),
                ('contact_no', models.CharField(max_length=50)),
                ('address', models.TextField()),
                ('city', models.CharField(max_length=26)),
                ('zipcode', models.CharField(max_length=26)),
            ],
            options={
                'verbose_name_plural': 'Employee',
                'ordering': ('-created_at',),
            },
        ),
    ]