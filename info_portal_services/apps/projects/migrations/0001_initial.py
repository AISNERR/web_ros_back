# Generated by Django 4.0.3 on 2022-07-06 11:28

from django.conf import settings
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=400)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='projects_created', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['created_at'],
            },
        ),
        migrations.CreateModel(
            name='ProjectItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='data_items_created', to=settings.AUTH_USER_MODEL)),
                ('polymorphic_ctype', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_%(app_label)s.%(class)s_set+', to='contenttypes.contenttype')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='projects.project')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
        ),
        migrations.CreateModel(
            name='ProjectTypes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alias', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='OilSpillContour',
            fields=[
                ('projectitem_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='projects.projectitem')),
                ('geom', django.contrib.gis.db.models.fields.PolygonField(srid=4326)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('projects.projectitem',),
        ),
        migrations.AddField(
            model_name='project',
            name='project_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects_of_type', to='projects.projecttypes'),
        ),
    ]
