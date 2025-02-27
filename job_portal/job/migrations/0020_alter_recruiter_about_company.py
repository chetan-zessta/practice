# Generated by Django 5.0.3 on 2024-05-06 09:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0019_alter_recruiter_about_company'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recruiter',
            name='about_company',
            field=models.CharField(default="Welcome to our company! We are dedicated to providing innovative solutions and excellent services to our clients. Our team consists of talented professionals who are passionate about their work and committed to achieving our company's goals. With a focus on quality and customer satisfaction, we strive to exceed expectations in everything we do. Explore our website to learn more about our company and the exciting opportunities we offer.", max_length=100),
        ),
    ]
