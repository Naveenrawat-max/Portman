# Generated by Django 5.1.4 on 2024-12-31 17:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portman', '0008_alter_profile_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='user',
            field=models.CharField(max_length=255),
        ),
    ]
