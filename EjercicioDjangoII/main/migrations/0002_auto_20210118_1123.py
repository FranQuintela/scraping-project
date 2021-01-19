# Generated by Django 3.1.2 on 2021-01-18 10:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='brand',
        ),
        migrations.RemoveField(
            model_name='product',
            name='type',
        ),
        migrations.AlterField(
            model_name='product',
            name='current_price',
            field=models.TextField(verbose_name='Color'),
        ),
        migrations.AlterField(
            model_name='product',
            name='old_price',
            field=models.TextField(verbose_name='Color'),
        ),
        migrations.AlterField(
            model_name='product',
            name='url',
            field=models.TextField(default='Undefined', verbose_name='Url'),
        ),
    ]