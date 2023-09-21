# Generated by Django 3.2.20 on 2023-09-21 23:20

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('credit', '0008_evidencerating'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='period',
        ),
        migrations.AddField(
            model_name='post',
            name='deadline',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
