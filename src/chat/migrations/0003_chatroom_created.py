# Generated by Django 4.2.5 on 2023-10-16 09:32

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_chatroom_message_room'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatroom',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
