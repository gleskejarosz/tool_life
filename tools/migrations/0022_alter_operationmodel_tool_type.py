# Generated by Django 3.2.15 on 2022-10-22 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0021_alter_operationmodel_tool_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='operationmodel',
            name='tool_type',
            field=models.CharField(choices=[('Tool', 'Tool'), ('Rubber', 'Rubber')], default='Tool', max_length=64),
        ),
    ]