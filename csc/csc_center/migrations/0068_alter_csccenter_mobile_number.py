# Generated by Django 5.0.6 on 2025-01-13 05:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csc_center', '0067_expiringcsccenter'),
    ]

    operations = [
        migrations.AlterField(
            model_name='csccenter',
            name='mobile_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
