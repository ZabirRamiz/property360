# Generated by Django 4.2.4 on 2023-08-21 08:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Hires',
            fields=[
                ('support_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='website.employee')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.user')),
            ],
            options={
                'unique_together': {('support_id', 'user_id')},
            },
        ),
    ]
