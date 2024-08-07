# Generated by Django 5.0.3 on 2024-04-22 21:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_alter_job_created_at_alter_job_salary'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='company_website',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='job',
            name='experience',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='hours',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='job',
            name='qualifications',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='job',
            name='responsibilities',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='job',
            name='working_model',
            field=models.CharField(choices=[('remote', 'Remote'), ('hybrid', 'Hybrid'), ('on-site', 'On Site'), ('unspecified', 'Unspecified')], default='unspecified', max_length=25),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='job',
            name='benefits',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='skills',
            field=models.TextField(blank=True),
        ),
    ]
