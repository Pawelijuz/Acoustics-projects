# Generated by Django 4.2.4 on 2024-01-05 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('komunikator', '0003_remove_task_title'),
    ]

    operations = [
        migrations.CreateModel(
            name='Parametr',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parametr', models.IntegerField(max_length=100)),
            ],
        ),
    ]
