# Generated by Django 4.0.3 on 2022-07-01 14:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('photo_gallery', '0004_galleryformats_gallerytypes_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='GalleryFormats',
        ),
        migrations.DeleteModel(
            name='GalleryTypes',
        ),
    ]
