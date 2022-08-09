# Generated by Django 4.0.6 on 2022-08-09 13:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0006_alter_project_components'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='catalog_version',
            field=models.CharField(default='CMS ARS 3.1', help_text='The Catalog version, for example, NIST 800-53r5', max_length=64),
        ),
        migrations.AlterField(
            model_name='project',
            name='impact_level',
            field=models.CharField(choices=[('low', 'Low'), ('moderate', 'Moderate'), ('high', 'High')], help_text='FISMA impact level of the project', max_length=20),
        ),
        migrations.CreateModel(
            name='Control',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('control_id', models.CharField(max_length=12)),
                ('control_label', models.CharField(max_length=12)),
                ('sort_id', models.CharField(max_length=12)),
                ('control_family', models.CharField(max_length=128)),
                ('title', models.CharField(max_length=124)),
                ('description', models.JSONField(help_text='Control description OSCAL JSON formatted.')),
                ('implementation', models.TextField(blank=True, help_text='Control implementation text.')),
                ('guidance', models.TextField(blank=True, help_text='Control guidance text.')),
                ('status', models.CharField(choices=[('not_started', 'Not started'), ('incomplete', 'Incomplete'), ('completed', 'Completed')], default='not_started', max_length=12)),
                ('responsibility', models.CharField(choices=[('allocated', 'Allocated'), ('shared', 'Shared'), ('inherited', 'Inherited')], default='allocated', max_length=12)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.project')),
            ],
        ),
    ]