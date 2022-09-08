# Generated by Django 4.1.1 on 2022-09-22 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogs', '0007_alter_catalog_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='controls',
            name='control_label',
            field=models.CharField(help_text='Catalog control label, for example AC-01', max_length=16),
        ),
        migrations.AlterField(
            model_name='controls',
            name='sort_id',
            field=models.CharField(help_text='Catalog ID used for sorting, for example ac-01', max_length=16),
        ),
    ]