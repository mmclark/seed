# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-11-07 17:04
from __future__ import unicode_literals

import autoslug.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seed', '0095_auto_20180920_1819'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attributeoption',
            name='value_source',
            field=models.IntegerField(choices=[(0, 'Assessed Raw'), (2, 'Assessed'), (1, 'Portfolio Raw'), (3, 'Portfolio'), (4, 'BuildingSnapshot'), (5, 'Green Button Raw')]),
        ),
        migrations.AlterField(
            model_name='buildingsnapshot',
            name='match_type',
            field=models.IntegerField(blank=True, choices=[(1, 'System Match'), (2, 'User Match'), (3, 'Possible Match')], db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='buildingsnapshot',
            name='source_type',
            field=models.IntegerField(blank=True, choices=[(0, 'Assessed Raw'), (2, 'Assessed'), (1, 'Portfolio Raw'), (3, 'Portfolio'), (4, 'BuildingSnapshot'), (5, 'Green Button Raw')], db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='column',
            name='data_type',
            field=models.CharField(default='None', max_length=64),
        ),
        migrations.AlterField(
            model_name='column',
            name='merge_protection',
            field=models.IntegerField(choices=[(0, 'Favor New'), (1, 'Favor Existing')], default=0),
        ),
        migrations.AlterField(
            model_name='column',
            name='shared_field_type',
            field=models.IntegerField(choices=[(0, 'None'), (1, 'Public')], default=0),
        ),
        migrations.AlterField(
            model_name='columnlistsetting',
            name='inventory_type',
            field=models.IntegerField(choices=[(0, 'Property'), (1, 'Tax Lot')], default=0),
        ),
        migrations.AlterField(
            model_name='columnlistsetting',
            name='settings_location',
            field=models.IntegerField(choices=[(0, 'List View Settings'), (1, 'Detail View Settings')], default=0),
        ),
        migrations.AlterField(
            model_name='columnmapping',
            name='source_type',
            field=models.IntegerField(blank=True, choices=[(0, 'Assessed Raw'), (2, 'Assessed'), (1, 'Portfolio Raw'), (3, 'Portfolio'), (4, 'BuildingSnapshot'), (5, 'Green Button Raw')], null=True),
        ),
        migrations.AlterField(
            model_name='compliance',
            name='compliance_type',
            field=models.CharField(choices=[('Benchmarking', 'Benchmarking'), ('Auditing', 'Auditing'), ('Retro Commissioning', 'Retro Commissioning')], default='Benchmarking', max_length=30, verbose_name='compliance_type'),
        ),
        migrations.AlterField(
            model_name='dataqualitycheck',
            name='name',
            field=models.CharField(default='Default Data Quality Check', max_length=255),
        ),
        migrations.AlterField(
            model_name='meter',
            name='energy_type',
            field=models.IntegerField(choices=[(1, 'Natural Gas'), (2, 'Electricity'), (3, 'Fuel Oil'), (4, 'Fuel Oil No. 1'), (5, 'Fuel Oil No. 2'), (6, 'Fuel Oil No. 4'), (7, 'Fuel Oil No. 5 and No. 6'), (8, 'District Steam'), (9, 'District Hot Water'), (10, 'District Chilled Water'), (11, 'Propane'), (12, 'Liquid Propane'), (13, 'Kerosene'), (14, 'Diesel'), (15, 'Coal'), (16, 'Coal Anthracite'), (17, 'Coal Bituminous'), (18, 'Coke'), (19, 'Wood'), (20, 'Other')]),
        ),
        migrations.AlterField(
            model_name='meter',
            name='energy_units',
            field=models.IntegerField(choices=[(1, 'kWh'), (2, 'Therms'), (3, 'Wh')]),
        ),
        migrations.AlterField(
            model_name='note',
            name='note_type',
            field=models.IntegerField(choices=[(0, 'Note'), (1, 'Log')], default=0, null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='slug',
            field=autoslug.fields.AutoSlugField(editable=True, populate_from='name', unique=True, verbose_name='slug'),
        ),
        migrations.AlterField(
            model_name='propertystate',
            name='data_state',
            field=models.IntegerField(choices=[(0, 'Unknown'), (1, 'Post Import'), (2, 'Post Mapping'), (3, 'Post Matching'), (4, 'Flagged for Deletion')], default=0),
        ),
        migrations.AlterField(
            model_name='propertystate',
            name='merge_state',
            field=models.IntegerField(choices=[(0, 'Unknown'), (1, 'New Record'), (2, 'Merged Record'), (3, 'Duplicate Record'), (4, 'Delete Record')], default=0, null=True),
        ),
        migrations.AlterField(
            model_name='rule',
            name='data_type',
            field=models.IntegerField(choices=[(0, 'number'), (1, 'string'), (2, 'date'), (3, 'year'), (4, 'area'), (5, 'eui')], null=True),
        ),
        migrations.AlterField(
            model_name='rule',
            name='rule_type',
            field=models.IntegerField(choices=[(0, 'default'), (1, 'custom')], null=True),
        ),
        migrations.AlterField(
            model_name='rule',
            name='severity',
            field=models.IntegerField(choices=[(0, 'error'), (1, 'warning')], default=0),
        ),
        migrations.AlterField(
            model_name='rule',
            name='table_name',
            field=models.CharField(blank=True, default='PropertyState', max_length=200),
        ),
        migrations.AlterField(
            model_name='statuslabel',
            name='color',
            field=models.CharField(choices=[('red', 'red'), ('blue', 'blue'), ('light blue', 'light blue'), ('green', 'green'), ('white', 'white'), ('orange', 'orange'), ('gray', 'gray')], default='green', max_length=30, verbose_name='compliance_type'),
        ),
        migrations.AlterField(
            model_name='taxlotstate',
            name='data_state',
            field=models.IntegerField(choices=[(0, 'Unknown'), (1, 'Post Import'), (2, 'Post Mapping'), (3, 'Post Matching'), (4, 'Flagged for Deletion')], default=0),
        ),
        migrations.AlterField(
            model_name='taxlotstate',
            name='merge_state',
            field=models.IntegerField(choices=[(0, 'Unknown'), (1, 'New Record'), (2, 'Merged Record'), (3, 'Duplicate Record'), (4, 'Delete Record')], default=0, null=True),
        ),
        migrations.AlterField(
            model_name='unit',
            name='unit_type',
            field=models.IntegerField(choices=[(1, 'String'), (6, 'Integer'), (3, 'Float'), (4, 'Date'), (5, 'Datetime')], default=1),
        ),
    ]