# Generated by Django 2.2.6 on 2020-01-13 02:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bitr24', '0008_remove_messages_chatm'),
    ]

    operations = [
        migrations.AddField(
            model_name='bitr',
            name='bx24_name',
            field=models.CharField(db_index=True, default='', max_length=100, verbose_name='Имя в Битрикс24'),
        ),
    ]
