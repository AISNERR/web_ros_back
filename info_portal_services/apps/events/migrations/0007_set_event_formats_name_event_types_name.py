# Generated by Django 4.0.3 on 2022-07-08 08:36

from django.db import migrations


def set_eventformats_name(apps, schema_editor):
    EventFormats = apps.get_model('events', 'EventFormats')
    EventFormats.objects.filter(event_format="online").update(name="онлайн")
    EventFormats.objects.filter(event_format="offline").update(name="офлайн")


def set_eventtypes_name(apps, schema_editor):
    EventTypes = apps.get_model('events', 'EventTypes')
    EventTypes.objects.filter(event_type="seminar").update(name="семинар")
    EventTypes.objects.filter(event_type="conference").update(name="конференция")
    EventTypes.objects.filter(event_type="lecture").update(name="лекция")


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0006_eventformats_name_eventtypes_name'),
    ]

    operations = [
        # omit reverse_code=... if you don't want the migration to be reversible.
        migrations.RunPython(set_eventformats_name, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(set_eventtypes_name, reverse_code=migrations.RunPython.noop),
    ]
