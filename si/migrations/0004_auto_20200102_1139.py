# Generated by Django 2.2.6 on 2020-01-02 11:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('si', '0003_auto_20190827_1939'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sith',
            name='planet',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='si.Planets', verbose_name='Планета'),
        ),
    ]
