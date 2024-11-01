# Generated by Django 5.1.2 on 2024-10-29 16:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recommendations',
            name='recommendation_id',
        ),
        migrations.AddField(
            model_name='recommendations',
            name='recommendation',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='recommendation', to='shop.salesman'),
        ),
        migrations.AlterField(
            model_name='recommendations',
            name='salesman',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='salesman', to='shop.salesman'),
        ),
    ]
