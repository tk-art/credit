# Generated by Django 3.2.20 on 2023-09-02 23:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('credit', '0005_auto_20230830_1339'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='follows',
            field=models.ManyToManyField(related_name='followed_by', to='credit.Profile'),
        ),
    ]
