# Generated by Django 3.2.16 on 2023-01-22 16:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0063_alter_operationmodel_machine'),
    ]

    operations = [
        migrations.AlterField(
            model_name='operationmodel',
            name='tool',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tools5', to='tools.toolstationmodel'),
        ),
    ]
