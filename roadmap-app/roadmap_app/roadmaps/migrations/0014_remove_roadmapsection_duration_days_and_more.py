# Generated by Django 5.1.5 on 2025-03-31 23:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roadmaps', '0013_roadmapsection_duration_days'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='roadmapsection',
            name='duration_days',
        ),
        migrations.AddField(
            model_name='roadmapsection',
            name='width_percentage',
            field=models.FloatField(null=True),
        ),
    ]
