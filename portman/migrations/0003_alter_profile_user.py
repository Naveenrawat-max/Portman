# Generated by Django 5.1.4 on 2024-12-28 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portman', '0002_education'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='user',
            field=models.CharField(max_length=255),
        ),
    ]
