# Generated by Django 4.0.6 on 2022-08-02 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogs', '0004_catalog_source'),
    ]

    operations = [
        migrations.AddField(
            model_name='catalog',
            name='impact_level',
            field=models.CharField(choices=[('low', 'Low'), ('moderate', 'Moderate'), ('high', 'High'), ('pii/phi', 'PII or PHI')], default='moderate', help_text='FISMA impact level of the project', max_length=20),
        ),
        migrations.AddField(
            model_name='catalog',
            name='version',
            field=models.CharField(default='CMS ARS 3.1', max_length=64),
        ),
    ]