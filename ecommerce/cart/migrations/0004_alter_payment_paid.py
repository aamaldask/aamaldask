# Generated by Django 5.1.2 on 2024-10-23 04:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0003_payment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='paid',
            field=models.BooleanField(default=False),
        ),
    ]
