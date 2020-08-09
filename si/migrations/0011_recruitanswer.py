# Generated by Django 2.2.11 on 2020-07-03 23:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('si', '0010_auto_20200526_0156'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecruitAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='recruitanswers', to='si.Answer', verbose_name='Ответ')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='recruitanswers', to='si.Test', verbose_name='Вопрос')),
                ('recruit', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='recruitanswers', to='si.Recruit', verbose_name='Рекрут')),
            ],
        ),
    ]