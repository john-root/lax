# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-09-05 16:03


from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('publisher', '0015_auto_20160412_1021'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalarticle',
            name='history_user',
        ),
        migrations.RemoveField(
            model_name='historicalarticle',
            name='journal',
        ),
        migrations.RemoveField(
            model_name='historicalarticleattribute',
            name='article',
        ),
        migrations.RemoveField(
            model_name='historicalarticleattribute',
            name='history_user',
        ),
        migrations.RemoveField(
            model_name='historicalarticleattribute',
            name='key',
        ),
        migrations.DeleteModel(
            name='HistoricalArticle',
        ),
        migrations.DeleteModel(
            name='HistoricalArticleAttribute',
        ),
    ]
