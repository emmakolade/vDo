# Generated by Django 4.2.6 on 2023-10-22 00:13

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=300)),
                ('description', models.TextField()),
                ('thumbnail_url', models.URLField()),
                ('video_url', models.URLField(unique=True)),
                ('video_id', models.CharField(max_length=40, unique=True)),
                ('downloaded_date', models.DateTimeField(auto_now_add=True)),
                ('uploaded_date', models.DateTimeField()),
            ],
        ),
    ]