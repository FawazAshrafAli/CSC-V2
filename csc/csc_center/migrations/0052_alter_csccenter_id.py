# Generated by Django 5.0.6 on 2024-10-05 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csc_center', '0051_alter_csccenter_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='csccenter',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
