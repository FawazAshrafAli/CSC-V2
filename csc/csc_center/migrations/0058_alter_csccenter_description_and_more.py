# Generated by Django 5.0.6 on 2024-11-23 12:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csc_center', '0057_csccenter_csc_reg_no'),
    ]

    operations = [
        migrations.AlterField(
            model_name='csccenter',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='csccenter',
            name='landmark_or_building_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='csccenter',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='csc_center_logos/'),
        ),
    ]
