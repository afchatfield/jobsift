# Generated by Django 5.0.3 on 2024-05-09 19:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_jobboardselector'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobboardselector',
            name='job_board',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='selectors', to='app.jobboard'),
        ),
        migrations.CreateModel(
            name='JobBoardSearchSelector',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('selector_type', models.CharField(choices=[('search_title', 'Search Title'), ('search_location', 'Search Location'), ('next_page', 'Next Page')], max_length=100)),
                ('css_selector', models.TextField()),
                ('job_board', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='search_selectors', to='app.jobboard')),
            ],
        ),
    ]
