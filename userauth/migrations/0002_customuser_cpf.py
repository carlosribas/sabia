# Generated by Django 3.1.4 on 2023-07-16 18:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauth', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='cpf',
            field=models.CharField(blank=True, max_length=15, verbose_name='CPF'),
        ),
    ]
