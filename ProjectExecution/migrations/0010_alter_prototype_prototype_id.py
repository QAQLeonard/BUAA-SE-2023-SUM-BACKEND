# Generated by Django 4.2.4 on 2023-09-01 03:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ProjectExecution', '0009_alter_project_project_image_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prototype',
            name='prototype_id',
            field=models.CharField(max_length=60, primary_key=True, serialize=False),
        ),
    ]
