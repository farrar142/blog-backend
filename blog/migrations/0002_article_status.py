# Generated by Django 4.0.2 on 2022-02-24 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='status',
            field=models.SmallIntegerField(blank=True, default=0, null=True, verbose_name='상태'),
        ),
    ]