# Generated by Django 5.0.3 on 2024-04-25 07:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0009_alter_recruiter_type_alter_studentuser_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recruiter',
            name='status',
            field=models.CharField(choices=[('reject', 'Reject'), ('accept', 'Accept')], max_length=20, null=True),
        ),
    ]
