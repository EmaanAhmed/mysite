# Generated by Django 3.1.5 on 2021-01-11 00:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contact',
            name='friends',
        ),
        migrations.AddField(
            model_name='contact',
            name='status',
            field=models.BooleanField(default=False),
        ),
    ]
