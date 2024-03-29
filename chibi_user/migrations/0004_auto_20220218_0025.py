# Generated by Django 3.0.3 on 2022-02-18 00:25

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_GROUP_MODEL),
        migrations.swappable_dependency(settings.AUTH_PERMISSION_MODEL),
        ('chibi_user', '0003_auto_20211210_2229'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='permissions',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_PERMISSION_MODEL, verbose_name='permissions'),
        ),
        migrations.AlterField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to=settings.AUTH_GROUP_MODEL, verbose_name='groups'),
        ),
        migrations.AlterField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to=settings.AUTH_PERMISSION_MODEL, verbose_name='user permissions'),
        ),
    ]
