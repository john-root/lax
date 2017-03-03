# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-02-21 05:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publisher', '0035_auto_20170221_0523'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articlefragment',
            name='version',
            field=models.PositiveSmallIntegerField(blank=True, help_text='if null, fragment applies only to a specific version of article', null=True),
        ),
    ]