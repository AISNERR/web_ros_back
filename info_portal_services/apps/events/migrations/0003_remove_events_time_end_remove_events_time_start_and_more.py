# Generated by Django 4.0.3 on 2022-05-27 09:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_alter_events_created_by_alter_events_modified_by_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='events',
            name='time_end',
        ),
        migrations.RemoveField(
            model_name='events',
            name='time_start',
        ),
        migrations.AlterField(
            model_name='events',
            name='date_end',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='events',
            name='date_start',
            field=models.DateTimeField(),
        ),
    ]
