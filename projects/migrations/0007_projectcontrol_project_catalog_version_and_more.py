# Generated by Django 4.1 on 2022-08-15 20:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalogs', '0005_catalog_impact_level_catalog_version_controls'),
        ('projects', '0006_alter_project_components'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectControl',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('not_started', 'Not started'), ('incomplete', 'Incomplete'), ('completed', 'Completed')], default='not_started', help_text='The Project Control status; completed, incomplete, or not started', max_length=20)),
                ('control', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='catalogs.controls')),
            ],
        ),
        migrations.AddField(
            model_name='project',
            name='catalog_version',
            field=models.CharField(default=None, help_text='The Catalog version, for example ARS 3.1', max_length=32),
        ),
        migrations.AddField(
            model_name='project',
            name='controls',
            field=models.ManyToManyField(related_name='project_controls', through='projects.ProjectControl', to='catalogs.controls'),
        ),
        migrations.AlterField(
            model_name='project',
            name='impact_level',
            field=models.CharField(choices=[('low', 'Low'), ('moderate', 'Moderate'), ('high', 'High')], default=None, help_text='FISMA impact level of the project', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='projectcontrol',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.project'),
        ),
    ]
