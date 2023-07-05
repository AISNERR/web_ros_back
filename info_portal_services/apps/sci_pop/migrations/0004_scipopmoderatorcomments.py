# Generated by Django 4.0.3 on 2022-07-11 16:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sci_pop', '0003_rename_ddate_video_scipop_date_video'),
    ]

    operations = [
        migrations.CreateModel(
            name='SciPopModeratorComments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField()),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sci_pop_comments_created', to=settings.AUTH_USER_MODEL)),
                ('sci_pop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sci_pop_comments', to='sci_pop.scipop')),
            ],
        ),
    ]
