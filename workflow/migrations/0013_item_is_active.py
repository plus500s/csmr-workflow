# Generated by Django 2.2.4 on 2019-09-16 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0012_auto_20190911_1233'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
    ]
