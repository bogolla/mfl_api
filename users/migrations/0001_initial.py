# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import django.contrib.postgres.fields
import oauth2_provider.validators
import django.contrib.auth.models
import oauth2_provider.generators
import django.utils.timezone
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='MflUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(unique=True, max_length=254)),
                ('first_name', models.CharField(max_length=60, blank=True)),
                ('last_name', models.CharField(max_length=60, blank=True)),
                ('other_names', models.CharField(default=b'', max_length=80, blank=True)),
                ('username', models.CharField(blank=True, max_length=60, unique=True, null=True, validators=[django.core.validators.RegexValidator(regex=b'^\\w+$', message=b'Preferred name contain only letters numbers or underscores')])),
                ('is_staff', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_national', models.BooleanField(default=False)),
                ('search', models.CharField(max_length=255, null=True, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('password_history', django.contrib.postgres.fields.ArrayField(size=None, null=True, base_field=models.TextField(null=True, blank=True), blank=True)),
                ('employee_number', models.CharField(unique=True, max_length=20)),
            ],
            options={
                'ordering': ('-date_joined',),
                'default_permissions': ('add', 'change', 'delete', 'view'),
            },
        ),
        migrations.CreateModel(
            name='CustomGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('regulator', models.BooleanField(default=False, help_text=b'Are the regulators in this group?')),
                ('national', models.BooleanField(default=False, help_text=b'Will the users in this group see all facilities in thecountry?')),
                ('administrator', models.BooleanField(default=False, help_text=b'Will the users in this group administrator user rights?')),
            ],
        ),
        migrations.CreateModel(
            name='MFLOAuthApplication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('client_id', models.CharField(default=oauth2_provider.generators.generate_client_id, unique=True, max_length=100, db_index=True)),
                ('redirect_uris', models.TextField(help_text='Allowed URIs list, space separated', blank=True, validators=[oauth2_provider.validators.validate_uris])),
                ('client_type', models.CharField(max_length=32, choices=[('confidential', 'Confidential'), ('public', 'Public')])),
                ('authorization_grant_type', models.CharField(max_length=32, choices=[('authorization-code', 'Authorization code'), ('implicit', 'Implicit'), ('password', 'Resource owner password-based'), ('client-credentials', 'Client credentials')])),
                ('client_secret', models.CharField(default=oauth2_provider.generators.generate_client_secret, max_length=255, db_index=True, blank=True)),
                ('name', models.CharField(max_length=255, blank=True)),
                ('skip_authorization', models.BooleanField(default=False)),
                ('user', models.ForeignKey(related_name='users_mfloauthapplication', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'default_permissions': ('add', 'change', 'delete', 'view'),
                'verbose_name': 'mfl oauth application',
                'verbose_name_plural': 'mfl oauth applications',
            },
        ),
        migrations.CreateModel(
            name='ProxyGroup',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('auth.group',),
            managers=[
                (b'objects', django.contrib.auth.models.GroupManager()),
            ],
        ),
        migrations.AddField(
            model_name='customgroup',
            name='group',
            field=models.OneToOneField(related_name='custom_group_fields', on_delete=django.db.models.deletion.PROTECT, to='auth.Group'),
        ),
        migrations.AddField(
            model_name='mfluser',
            name='groups',
            field=models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='mfluser',
            name='user_permissions',
            field=models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions'),
        ),
    ]
