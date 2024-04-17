# Generated by Django 5.0.3 on 2024-04-17 11:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Camera',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('stream_url', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='Caption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sentence', models.TextField(null=True)),
                ('sentiment_score', models.TextField(null=True)),
                ('sentiment_result', models.CharField(choices=[('P', 'Positive'), ('N', 'Negative'), ('U', 'Unknown')], default='U', max_length=1, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('camera', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='camera.camera')),
            ],
        ),
        migrations.CreateModel(
            name='RiskySection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('video_uid', models.TextField(null=True)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('camera', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='camera.camera')),
            ],
        ),
    ]
