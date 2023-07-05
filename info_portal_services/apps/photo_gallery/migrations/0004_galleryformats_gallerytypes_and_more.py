# Generated by Django 4.0.3 on 2022-06-30 14:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('status_model', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('photo_gallery', '0003_alter_postingallery_location'),
    ]

    operations = [
        migrations.CreateModel(
            name='GalleryFormats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo_gallery_format', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='GalleryTypes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo_gallery_type', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='postingallery',
            name='photo_gallery_status',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='photo_gallery_in_status', to='status_model.statustypes'),
        ),
        migrations.CreateModel(
            name='GalleryModeratorComments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField()),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='photo_gallery_comments_created', to=settings.AUTH_USER_MODEL)),
                ('photo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photo_gallery_comments', to='photo_gallery.postingallery')),
            ],
        ),
    ]