# Generated by Django 3.2.5 on 2021-07-22 19:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bagdiscovery', '0007_auto_20210721_1813'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bag',
            name='process_status',
            field=models.IntegerField(choices=[(1, 'Created'), (2, 'Discovered'), (3, 'Delivered')], default=1),
        ),
    ]