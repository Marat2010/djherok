# Generated by Django 2.2.11 on 2020-07-15 13:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('si', '0015_auto_20200712_1319'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recruitanswer',
            name='answer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='recruitanswers', to='si.Answer', verbose_name='Ответ'),
        ),
    ]
