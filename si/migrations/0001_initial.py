# Generated by Django 2.2.4 on 2019-08-25 20:15

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Planets',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Tests',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_code', models.IntegerField(unique=True)),
                ('list_questions', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Sith',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('planet', models.ForeignKey(on_delete=models.SET('hehe'), to='si.Planets')),
            ],
        ),
        migrations.CreateModel(
            name='Recruits',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('age', models.IntegerField(default=1)),
                ('email', models.EmailField(max_length=50, unique=True)),
                ('planet', models.ForeignKey(on_delete=models.SET('hehe'), to='si.Planets')),
            ],
        ),
    ]
