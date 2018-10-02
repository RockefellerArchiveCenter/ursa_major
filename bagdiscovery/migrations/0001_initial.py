# Generated by Django 2.0 on 2018-10-02 23:12

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Accession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('archivesspace_identifier', models.CharField(blank=True, max_length=255, null=True)),
                ('data', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now=True)),
                ('last_modified', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Bag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bag_identifier', models.CharField(max_length=255)),
                ('bag_path', models.CharField(blank=True, max_length=255, null=True)),
                ('archivesspace_identifier', models.CharField(blank=True, max_length=255, null=True)),
                ('data', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now=True)),
                ('last_modified', models.DateTimeField(auto_now_add=True)),
                ('accession', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bagdiscovery.Accession')),
            ],
        ),
    ]
