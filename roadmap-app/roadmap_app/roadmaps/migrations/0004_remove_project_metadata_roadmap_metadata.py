# Generated by Django 5.1.5 on 2025-02-03 22:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roadmaps', '0003_project_metadata'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='metadata',
        ),
        migrations.AddField(
            model_name='roadmap',
            name='metadata',
            field=models.JSONField(default=dict),
        ),
    ]
