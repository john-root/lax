# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-10-11 15:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publisher', '0026_articlefragment'),
    ]

    operations = [
        migrations.AddField(
            model_name='articlefragment',
            name='position',
            field=models.PositiveSmallIntegerField(default=1, help_text=b'position in the merge order with lower fragments merged first'),
        ),
        migrations.AddField(
            model_name='articlefragment',
            name='type',
            field=models.CharField(default=None, help_text=b'the type of fragment, eg "xml", "content-header", etc', max_length=25, unique=True),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='articlefragment',
            unique_together=set([('article', 'type')]),
        ),
    ]
