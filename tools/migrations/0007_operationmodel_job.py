# Generated by Django 3.2.15 on 2022-10-14 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0006_auto_20221014_1306'),
    ]

    operations = [
        migrations.AddField(
            model_name='operationmodel',
            name='job',
            field=models.ManyToManyField(to='tools.RelationModel'),
        ),
    ]
