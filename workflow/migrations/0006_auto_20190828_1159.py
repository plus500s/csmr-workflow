# Generated by Django 2.2.4 on 2019-08-28 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0005_auto_20190828_1154'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rater',
            name='email',
            field=models.EmailField(max_length=254, null=True, unique=True),
        ),
    ]
