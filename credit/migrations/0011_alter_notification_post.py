# Generated by Django 3.2.20 on 2023-09-23 23:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('credit', '0010_notification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='post',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='credit.post'),
        ),
    ]
