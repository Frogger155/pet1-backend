# Generated by Django 4.2.7 on 2024-01-15 08:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0005_like'),
    ]

    operations = [
        migrations.AddField(
            model_name='like',
            name='post',
            field=models.ForeignKey(default='1', on_delete=django.db.models.deletion.CASCADE, to='posts.post'),
        ),
    ]
