# Generated by Django 4.1.1 on 2022-09-27 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0008_alter_project_catalog_version_alter_project_creator_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectcontrol',
            name='status',
            field=models.CharField(choices=[('not_started', 'Not started'), ('incomplete', 'Incomplete'), ('complete', 'Complete')], default='not_started', help_text='The Project Control status; completed, incomplete, or not started', max_length=20),
        ),
    ]
