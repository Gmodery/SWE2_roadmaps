# Generated by Django 5.1.5 on 2025-03-28 18:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roadmaps', '0007_roadmap_parent_project_alter_project_class_instance'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskcategory',
            name='task_color',
            field=models.CharField(default='ffffff', max_length=6),
        ),
        migrations.AddField(
            model_name='taskcategory',
            name='task_roadmap',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='roadmaps.roadmap'),
        ),
    ]
