# Generated by Django 4.2.4 on 2023-08-28 03:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TeamManagement', '0002_alter_chatgroup_group_id_alter_message_message_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='message_id',
            field=models.CharField(max_length=60, primary_key=True, serialize=False),
        ),
    ]
