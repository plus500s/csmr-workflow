# Generated by Django 2.2.4 on 2019-08-29 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0006_auto_20190828_1159'),
    ]

    operations = [
        migrations.AddField(
            model_name='workflow',
            name='corroborating_question',
            field=models.TextField(default='Were you able to find any corroborating evidence?'),
        ),
    ]
