# Generated by Django 2.2.11 on 2020-07-19 17:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('si', '0018_auto_20200719_1846'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recruit',
            name='answers',
        ),
    ]
