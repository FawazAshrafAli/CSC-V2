# Generated by Django 5.0.6 on 2024-11-28 09:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('csc_center', '0061_csccenter_inactive_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='csccenter',
            name='inactive_date',
        ),
        migrations.RemoveField(
            model_name='csccenter',
            name='payment_implemented_date',
        ),
    ]
