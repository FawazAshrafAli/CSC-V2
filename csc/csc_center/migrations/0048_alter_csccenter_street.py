# Generated by Django 5.0.6 on 2024-10-02 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csc_center', '0047_alter_csccenter_street'),
    ]

    operations = [
        migrations.AlterField(
            model_name='csccenter',
            name='street',
            field=models.CharField(max_length=500),
        ),
    ]
