# Generated by Django 4.0.2 on 2022-02-27 20:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_article_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='deleted_at',
            field=models.DateTimeField(default=None, null=True, verbose_name='삭제일'),
        ),
        migrations.AddField(
            model_name='blog',
            name='deleted_at',
            field=models.DateTimeField(default=None, null=True, verbose_name='삭제일'),
        ),
        migrations.AlterField(
            model_name='article',
            name='update_date',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='수정날짜'),
        ),
        migrations.AlterField(
            model_name='blog',
            name='reg_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='등록날짜'),
        ),
        migrations.AlterField(
            model_name='blog',
            name='update_date',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='수정날짜'),
        ),
    ]
