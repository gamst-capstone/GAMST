# Generated by Django 5.0.3 on 2024-04-10 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0007_rename_cropped_sentence_caption_sentence_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='riskysection',
            name='video_uid',
            field=models.TextField(null=True),
        ),
    ]