# Generated by Django 5.1.7 on 2025-03-23 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0019_alter_restaraunt_latitude_alter_restaraunt_longitude_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='restaraunt',
            name='latitude',
            field=models.DecimalField(blank=True, db_column='latitude', decimal_places=10, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='restaraunt',
            name='longitude',
            field=models.DecimalField(blank=True, db_column='longitude', decimal_places=10, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='userregister',
            name='latitude',
            field=models.DecimalField(blank=True, db_column='latitude', decimal_places=10, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='userregister',
            name='longitude',
            field=models.DecimalField(blank=True, db_column='longitude', decimal_places=10, max_digits=10, null=True),
        ),
    ]
