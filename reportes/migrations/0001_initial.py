# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-16 18:48
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Reporte',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, unique=True)),
                ('user_id', models.ManyToManyField(related_name='user_id', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]