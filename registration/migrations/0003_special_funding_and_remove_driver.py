# Generated manually — 18 July 2026 fee/policy update:
# removes the driver add-on and introduces Special Funding contributions.

from django.db import migrations, models
import registration.models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0002_fee_upgrade_fields'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='registrant',
            name='is_driver',
        ),
        migrations.CreateModel(
            name='SpecialFunding',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('funding_type', models.CharField(choices=[('individual', 'Individual'), ('batch', 'Batch')], max_length=10)),
                ('ssc_batch', models.PositiveIntegerField(blank=True, null=True)),
                ('contributor_name', models.CharField(blank=True, max_length=150, null=True)),
                ('contributor_phone', models.CharField(blank=True, max_length=20, null=True)),
                ('amount', models.PositiveIntegerField(help_text='Contribution amount in Taka')),
                ('funding_id', models.CharField(default=registration.models.generate_funding_id, editable=False, max_length=30, unique=True)),
                ('payment_status', models.CharField(choices=[('pending', 'Pending'), ('paid', 'Paid'), ('failed', 'Failed'), ('cancelled', 'Cancelled')], default='pending', max_length=10)),
                ('transaction_id', models.CharField(max_length=64, unique=True)),
                ('sslcz_val_id', models.CharField(blank=True, max_length=100, null=True)),
                ('sslcz_bank_tran_id', models.CharField(blank=True, max_length=100, null=True)),
                ('sslcz_card_type', models.CharField(blank=True, max_length=50, null=True)),
                ('paid_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Special Funding',
                'verbose_name_plural': 'Special Funding',
                'ordering': ['-created_at'],
            },
        ),
    ]
