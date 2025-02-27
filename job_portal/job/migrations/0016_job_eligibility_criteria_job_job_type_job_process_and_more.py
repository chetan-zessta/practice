# Generated by Django 5.0.3 on 2024-05-06 09:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0015_apply'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='eligibility_criteria',
            field=models.CharField(default='No specific eligibility criteria provided', max_length=300),
        ),
        migrations.AddField(
            model_name='job',
            name='job_type',
            field=models.CharField(default='Full-time', max_length=100),
        ),
        migrations.AddField(
            model_name='job',
            name='process',
            field=models.CharField(default='Standard application process', max_length=300),
        ),
        migrations.AlterField(
            model_name='job',
            name='description',
            field=models.TextField(),
        ),
    ]
