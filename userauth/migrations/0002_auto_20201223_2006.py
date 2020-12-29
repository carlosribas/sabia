# Generated by Django 3.1.4 on 2020-12-23 20:06

import django.core.validators
from django.db import migrations, models
import userauth.models


class Migration(migrations.Migration):

    dependencies = [
        ('userauth', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='academic_background',
            field=models.CharField(choices=[('vet', 'Veterinarian'), ('student', 'Veterinary medicine student'), ('other', 'Others')], default='vet', max_length=30, verbose_name='Academic background'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='customuser',
            name='certificate',
            field=models.FileField(blank=True, null=True, upload_to=userauth.models.user_directory_path, verbose_name='Certificate'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='other',
            field=models.CharField(blank=True, max_length=100, verbose_name='Other'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='phone',
            field=models.CharField(blank=True, default='', max_length=15, validators=[django.core.validators.RegexValidator(message='Enter a valid phone number starting with (DDD)', regex='^\\(?[1-9]{2}\\)? ?(?:[2-8]|9[1-9])[0-9]{3}\\-?[0-9]{4}$')], verbose_name='Phone'),
            preserve_default=False,
        ),
    ]