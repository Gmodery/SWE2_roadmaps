# Generated by Django 5.1.5 on 2025-03-24 18:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roadmaps', '0002_taskcategory_project_project_description_task'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='task_cat', to='roadmaps.taskcategory'),
        ),
    ]
