# Generated by Django 5.1.5 on 2025-03-28 20:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roadmaps', '0009_rename_task_color_taskcategory_cat_color_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='roadmap',
            name='metadata',
        ),
        migrations.AddField(
            model_name='roadmap',
            name='deadline',
            field=models.DateField(auto_now_add=True, null=True),
        ),
    ]
