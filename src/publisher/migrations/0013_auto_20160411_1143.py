# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-04-11 11:43


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publisher', '0012_auto_20160405_1746'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='datetime_accepted',
        ),
        migrations.RemoveField(
            model_name='historicalarticle',
            name='datetime_accepted',
        ),
        migrations.AddField(
            model_name='article',
            name='date_full_decision',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='date_full_qc',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='date_initial_decision',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='date_initial_qc',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='date_rev1_decision',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='date_rev1_qc',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='date_rev2_decision',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='date_rev2_qc',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='date_rev3_decision',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='date_rev3_qc',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='date_rev4_decision',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='date_rev4_qc',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='decision',
            field=models.CharField(blank=True, choices=[(b'RJI', b'Reject Initial Submission'), (b'RJF', b'Reject Full Submission'), (b'RVF', b'Revise Full Submission'), (b'AF', b'Accept Full Submission'), (b'EF', b'Encourage Full Submission'), (b'SW', b'Simple Withdraw')], max_length=25, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='ejp_type',
            field=models.CharField(blank=True, choices=[(b'RA', b'Research article'), (b'SR', b'Short report'), (b'AV', b'Research advance'), (b'RR', b'Registered report'), (b'TR', b'Tools and resources')], help_text=b'article as exported from EJP submission system', max_length=3, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='initial_decision',
            field=models.CharField(blank=True, choices=[(b'RJI', b'Reject Initial Submission'), (b'RJF', b'Reject Full Submission'), (b'RVF', b'Revise Full Submission'), (b'AF', b'Accept Full Submission'), (b'EF', b'Encourage Full Submission'), (b'SW', b'Simple Withdraw')], max_length=25, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='rev1_decision',
            field=models.CharField(blank=True, choices=[(b'RJI', b'Reject Initial Submission'), (b'RJF', b'Reject Full Submission'), (b'RVF', b'Revise Full Submission'), (b'AF', b'Accept Full Submission'), (b'EF', b'Encourage Full Submission'), (b'SW', b'Simple Withdraw')], max_length=25, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='rev2_decision',
            field=models.CharField(blank=True, choices=[(b'RJI', b'Reject Initial Submission'), (b'RJF', b'Reject Full Submission'), (b'RVF', b'Revise Full Submission'), (b'AF', b'Accept Full Submission'), (b'EF', b'Encourage Full Submission'), (b'SW', b'Simple Withdraw')], max_length=25, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='rev3_decision',
            field=models.CharField(blank=True, choices=[(b'RJI', b'Reject Initial Submission'), (b'RJF', b'Reject Full Submission'), (b'RVF', b'Revise Full Submission'), (b'AF', b'Accept Full Submission'), (b'EF', b'Encourage Full Submission'), (b'SW', b'Simple Withdraw')], max_length=25, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='rev4_decision',
            field=models.CharField(blank=True, choices=[(b'RJI', b'Reject Initial Submission'), (b'RJF', b'Reject Full Submission'), (b'RVF', b'Revise Full Submission'), (b'AF', b'Accept Full Submission'), (b'EF', b'Encourage Full Submission'), (b'SW', b'Simple Withdraw')], max_length=25, null=True),
        ),
        migrations.AddField(
            model_name='historicalarticle',
            name='date_full_decision',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicalarticle',
            name='date_full_qc',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicalarticle',
            name='date_initial_decision',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicalarticle',
            name='date_initial_qc',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicalarticle',
            name='date_rev1_decision',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicalarticle',
            name='date_rev1_qc',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicalarticle',
            name='date_rev2_decision',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicalarticle',
            name='date_rev2_qc',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicalarticle',
            name='date_rev3_decision',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicalarticle',
            name='date_rev3_qc',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicalarticle',
            name='date_rev4_decision',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicalarticle',
            name='date_rev4_qc',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicalarticle',
            name='decision',
            field=models.CharField(blank=True, choices=[(b'RJI', b'Reject Initial Submission'), (b'RJF', b'Reject Full Submission'), (b'RVF', b'Revise Full Submission'), (b'AF', b'Accept Full Submission'), (b'EF', b'Encourage Full Submission'), (b'SW', b'Simple Withdraw')], max_length=25, null=True),
        ),
        migrations.AddField(
            model_name='historicalarticle',
            name='ejp_type',
            field=models.CharField(blank=True, choices=[(b'RA', b'Research article'), (b'SR', b'Short report'), (b'AV', b'Research advance'), (b'RR', b'Registered report'), (b'TR', b'Tools and resources')], help_text=b'article as exported from EJP submission system', max_length=3, null=True),
        ),
        migrations.AddField(
            model_name='historicalarticle',
            name='initial_decision',
            field=models.CharField(blank=True, choices=[(b'RJI', b'Reject Initial Submission'), (b'RJF', b'Reject Full Submission'), (b'RVF', b'Revise Full Submission'), (b'AF', b'Accept Full Submission'), (b'EF', b'Encourage Full Submission'), (b'SW', b'Simple Withdraw')], max_length=25, null=True),
        ),
        migrations.AddField(
            model_name='historicalarticle',
            name='rev1_decision',
            field=models.CharField(blank=True, choices=[(b'RJI', b'Reject Initial Submission'), (b'RJF', b'Reject Full Submission'), (b'RVF', b'Revise Full Submission'), (b'AF', b'Accept Full Submission'), (b'EF', b'Encourage Full Submission'), (b'SW', b'Simple Withdraw')], max_length=25, null=True),
        ),
        migrations.AddField(
            model_name='historicalarticle',
            name='rev2_decision',
            field=models.CharField(blank=True, choices=[(b'RJI', b'Reject Initial Submission'), (b'RJF', b'Reject Full Submission'), (b'RVF', b'Revise Full Submission'), (b'AF', b'Accept Full Submission'), (b'EF', b'Encourage Full Submission'), (b'SW', b'Simple Withdraw')], max_length=25, null=True),
        ),
        migrations.AddField(
            model_name='historicalarticle',
            name='rev3_decision',
            field=models.CharField(blank=True, choices=[(b'RJI', b'Reject Initial Submission'), (b'RJF', b'Reject Full Submission'), (b'RVF', b'Revise Full Submission'), (b'AF', b'Accept Full Submission'), (b'EF', b'Encourage Full Submission'), (b'SW', b'Simple Withdraw')], max_length=25, null=True),
        ),
        migrations.AddField(
            model_name='historicalarticle',
            name='rev4_decision',
            field=models.CharField(blank=True, choices=[(b'RJI', b'Reject Initial Submission'), (b'RJF', b'Reject Full Submission'), (b'RVF', b'Revise Full Submission'), (b'AF', b'Accept Full Submission'), (b'EF', b'Encourage Full Submission'), (b'SW', b'Simple Withdraw')], max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='type',
            field=models.CharField(blank=True, help_text=b'xml article-type.', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='historicalarticle',
            name='type',
            field=models.CharField(blank=True, help_text=b'xml article-type.', max_length=50, null=True),
        ),
    ]
