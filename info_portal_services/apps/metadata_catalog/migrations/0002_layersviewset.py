# Generated by Django 4.0.3 on 2022-06-23 12:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('metadata_catalog', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LayersViewSet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('layers_tree', models.JSONField()),
                ('layers', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='viewset_in_layers', to='metadata_catalog.layers')),
            ],
        ),
    ]
