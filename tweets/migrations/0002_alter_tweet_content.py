# Generated by Django 3.2.6 on 2021-09-04 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tweets', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tweet',
            name='content',
            field=models.CharField(max_length=255, verbose_name=''),
        ),
    ]
