# Generated by Django 2.1.2 on 2018-11-04 21:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0007_auto_20181104_1208'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='user',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='drinking',
            name='user',
            field=models.PositiveIntegerField(),
        ),
    ]
