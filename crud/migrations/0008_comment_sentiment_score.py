# Generated by Django 3.2.18 on 2023-04-13 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crud', '0007_auto_20230413_1706'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='sentiment_score',
            field=models.FloatField(default=0.0),
        ),
    ]