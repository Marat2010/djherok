# Generated by Django 2.2.4 on 2019-08-26 21:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('si', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recruits',
            name='planet',
            field=models.ForeignKey(on_delete=models.SET('hehe'), related_name='entries', to='si.Planets'),
        ),
    ]