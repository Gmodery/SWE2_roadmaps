# Generated by Django 5.1.5 on 2025-04-01 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roadmaps', '0014_remove_roadmapsection_duration_days_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='roadmapsection',
            name='start_percent',
            field=models.FloatField(null=True),
        ),
    ]
