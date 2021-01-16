# Generated by Django 3.1.5 on 2021-01-12 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0005_remove_chat_seen_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='seen_by',
            field=models.ManyToManyField(related_name='seen_by', to='chat.Contact'),
        ),
    ]
