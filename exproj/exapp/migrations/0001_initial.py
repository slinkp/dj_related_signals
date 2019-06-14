# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='CustomerCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='CustomerCategoryRel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('category', models.ForeignKey(to='exapp.CustomerCategory')),
                ('customer', models.ForeignKey(to='exapp.Customer')),
            ],
        ),
        migrations.CreateModel(
            name='CustomerExtraJunk',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('customer', models.OneToOneField(related_name='extrajunk', null=True, to='exapp.Customer')),
            ],
        ),
        migrations.AddField(
            model_name='customer',
            name='categories_direct',
            field=models.ManyToManyField(related_name='customers_direct', to='exapp.CustomerCategory'),
        ),
        migrations.AddField(
            model_name='customer',
            name='categories_indirect',
            field=models.ManyToManyField(related_name='customers_indirect', through='exapp.CustomerCategoryRel', to='exapp.CustomerCategory'),
        ),
        migrations.AddField(
            model_name='customer',
            name='company',
            field=models.ForeignKey(related_name='customers', to='exapp.Company', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='customercategoryrel',
            unique_together=set([('customer', 'category')]),
        ),
    ]
