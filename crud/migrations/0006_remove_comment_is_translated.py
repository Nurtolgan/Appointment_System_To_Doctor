# Generated by Django 3.2.18 on 2023-04-13 11:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crud', '0005_auto_20230413_1531'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='is_translated',
        ),
    ]
