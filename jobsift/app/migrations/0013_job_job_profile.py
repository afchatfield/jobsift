# Generated by Django 5.0.3 on 2024-06-11 15:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_rename_color_jobprofile_colour_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='job_profile',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='app.jobprofile'),
        ),
    ]