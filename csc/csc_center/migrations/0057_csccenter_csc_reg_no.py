# Generated by Django 5.0.6 on 2024-10-28 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csc_center', '0056_csckeyword_created_csckeyword_updated'),
    ]

    operations = [
        migrations.AddField(
            model_name='csccenter',
            name='csc_reg_no',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
