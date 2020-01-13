# Generated by Django 2.2.6 on 2020-01-11 00:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bitr24', '0006_auto_20200110_2213'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bitr',
            name='chatB',
        ),
        migrations.AddField(
            model_name='bitr',
            name='slug',
            field=models.SlugField(default='', max_length=100, unique=True, verbose_name='Slug'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='chats',
            name='bitrs',
            field=models.ManyToManyField(blank=True, related_name='chats', to='bitr24.Bitr'),
        ),
    ]
