# Generated by Django 4.2.4 on 2023-09-02 06:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ProjectExecution', '0013_alter_doc_project'),
    ]

    operations = [
        migrations.AlterField(
            model_name='node',
            name='node_id',
            field=models.CharField(max_length=60, primary_key=True, serialize=False),
        ),
    ]
