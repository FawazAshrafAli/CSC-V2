# Generated by Django 5.0.6 on 2024-12-21 06:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0009_remove_commonservicecenter_map_iframe'),
    ]

    operations = [
        migrations.CreateModel(
            name='Banners',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='home_page_banner_image/')),
            ],
            options={
                'db_table': 'home_page_banner_image',
            },
        ),
        migrations.CreateModel(
            name='HomePageBanner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('images', models.ManyToManyField(to='home.banners')),
            ],
            options={
                'db_table': 'home_page_banners',
            },
        ),
    ]
