# Generated by Django 2.2.4 on 2019-10-10 08:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0022_auto_20191009_1544'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='rater_answer_judgment_misleading_item',
            field=models.TextField(blank=True, null=True),
        ),
    ]
