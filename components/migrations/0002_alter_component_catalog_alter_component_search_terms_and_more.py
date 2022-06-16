# Generated by Django 4.0.4 on 2022-06-16 03:53

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalogs', '0001_initial'),
        ('components', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='component',
            name='catalog',
            field=models.ForeignKey(help_text='Catalog id that this component applies to', on_delete=django.db.models.deletion.PROTECT, related_name='components_for_catalog', to='catalogs.catalog'),
        ),
        migrations.AlterField(
            model_name='component',
            name='search_terms',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=50), help_text='List of keywords to search for the component', null=True, size=None),
        ),
        migrations.AlterField(
            model_name='component',
            name='type',
            field=models.CharField(help_text='Type category of the component', max_length=100),
        ),
    ]
