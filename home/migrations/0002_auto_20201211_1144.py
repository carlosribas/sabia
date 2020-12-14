# Generated by Django 3.1.4 on 2020-12-11 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='homepagecarouselimages',
            name='description_color',
            field=models.CharField(blank=True, help_text='For example: #ffffff', max_length=7, verbose_name='Description color'),
        ),
        migrations.AddField(
            model_name='homepagecarouselimages',
            name='link',
            field=models.CharField(blank=True, help_text='URL to link to, e.g. /contato', max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='homepagecarouselimages',
            name='title_color',
            field=models.CharField(blank=True, help_text='For example: #ffffff', max_length=7, verbose_name='Title color'),
        ),
    ]