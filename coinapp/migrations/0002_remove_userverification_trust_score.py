# Generated by Django 5.1.1 on 2025-05-01 06:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coinapp', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userverification',
            name='trust_score',
        ),
    ]
