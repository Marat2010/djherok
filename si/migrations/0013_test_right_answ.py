# Generated by Django 2.2.11 on 2020-07-08 10:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('si', '0012_auto_20200708_0208'),
    ]

    operations = [
        migrations.AddField(
            model_name='test',
            name='right_answ',
            field=models.ManyToManyField(blank=True, related_name='tests_right', to='si.Answer', verbose_name='Правильный ответ'),
        ),
    ]
