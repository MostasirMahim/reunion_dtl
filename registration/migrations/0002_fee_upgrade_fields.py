# Generated manually for the fee/field upgrade (July 2026)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='registrant',
            old_name='department_class',
            new_name='last_class_attended',
        ),
        migrations.RenameField(
            model_name='registrant',
            old_name='passing_year',
            new_name='ssc_batch',
        ),
        migrations.AlterField(
            model_name='registrant',
            name='last_class_attended',
            field=models.CharField(help_text='e.g. Class 10 / SSC / Science-A', max_length=100),
        ),
        migrations.AlterField(
            model_name='registrant',
            name='ssc_batch',
            field=models.PositiveIntegerField(help_text='SSC Batch year. If not yet passed, the year you would/will pass.'),
        ),
        migrations.AlterField(
            model_name='registrant',
            name='phone',
            field=models.CharField(help_text='Primary mobile number (mandatory)', max_length=20),
        ),
        migrations.AddField(
            model_name='registrant',
            name='secondary_phone',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='registrant',
            name='whatsapp_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='registrant',
            name='ssc_passing_year',
            field=models.PositiveIntegerField(blank=True, help_text='Actual SSC passing year (optional)', null=True),
        ),
        migrations.AddField(
            model_name='registrant',
            name='is_driver',
            field=models.BooleanField(default=False, help_text='Bringing own driver (+৳500, lunch only)'),
        ),
    ]
