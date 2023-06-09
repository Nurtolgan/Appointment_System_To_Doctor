# Generated by Django 3.2.18 on 2023-04-13 10:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('crud', '0003_zapis'),
    ]

    operations = [
        migrations.AddField(
            model_name='zapis',
            name='is_translated',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='zapis',
            name='post',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='appointments', to='crud.post'),
        ),
    ]
