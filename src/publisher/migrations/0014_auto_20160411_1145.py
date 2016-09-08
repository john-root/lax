# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-04-11 11:45
from __future__ import unicode_literals

from django.db import migrations, models
from publisher import utils

def mkdoi(apps, schema_editor):
    Article = apps.get_model('publisher', 'Article')
    #HistoricalArticle = apps.get_model('publisher', 'HistoricalArticle')
    def update(art):
        msid = utils.doi2msid(art.doi)
        assert msid, "msid cannot be null. got %r for %r" % (msid, art)
        art.manuscript_id = msid
        art.save()
        return art
    map(update, Article.objects.all())

def unmkdoi(apps, schema_editor):
    Article = apps.get_model('publisher', 'Article')
    Article.objects.update(manuscript_id=None)
    
class Migration(migrations.Migration):
    
    dependencies = [
        ('publisher', '0013_auto_20160411_1143'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='manuscript_id',
            field=models.PositiveIntegerField(default=None, null=True, blank=True, help_text=b'article identifier from beginning of submission process right through to end of publication.'),
            preserve_default=False,
        ),

        migrations.AddField(
            model_name='historicalarticle',
            name='manuscript_id',
            field=models.PositiveIntegerField(db_index=True, default=1, help_text=b'article identifier from beginning of submission process right through to end of publication.'),
            preserve_default=False,
        ),

        migrations.RunPython(mkdoi, unmkdoi),

        migrations.AlterField(
            model_name='article',
            name='manuscript_id',
            field=models.PositiveIntegerField(unique=True, help_text=b'article identifier from beginning of submission process right through to end of publication.')
        ),

    ]
