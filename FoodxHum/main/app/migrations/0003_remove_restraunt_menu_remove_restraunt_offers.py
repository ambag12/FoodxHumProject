# Generated by Django 5.1.7 on 2025-03-09 13:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_restraunt_alter_userregister_options'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='restraunt',
            name='menu',
        ),
        migrations.RemoveField(
            model_name='restraunt',
            name='offers',
        ),
    ]
