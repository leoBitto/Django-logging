# Generated by Django 5.0 on 2024-02-10 14:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logging_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccessLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.CharField(max_length=45)),
                ('timestamp', models.DateTimeField()),
                ('request_path', models.CharField(max_length=255)),
                ('request_method', models.CharField(max_length=10)),
                ('response_code', models.PositiveIntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ErrorLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.CharField(max_length=45)),
                ('timestamp', models.DateTimeField()),
                ('request_path', models.CharField(max_length=255)),
                ('request_method', models.CharField(max_length=10)),
                ('response_code', models.PositiveIntegerField()),
                ('error_message', models.TextField()),
                ('stack_trace', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.DeleteModel(
            name='LogEntry',
        ),
    ]
