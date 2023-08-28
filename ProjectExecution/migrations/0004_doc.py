# Generated by Django 4.2.4 on 2023-08-28 01:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ProjectExecution', '0003_alter_project_project_id_prototype'),
    ]

    operations = [
        migrations.CreateModel(
            name='Doc',
            fields=[
                ('doc_id', models.CharField(max_length=40, primary_key=True, serialize=False)),
                ('editable_by_guests', models.BooleanField(default=False)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ProjectExecution.project')),
            ],
            options={
                'db_table': 'Docs',
            },
        ),
    ]
