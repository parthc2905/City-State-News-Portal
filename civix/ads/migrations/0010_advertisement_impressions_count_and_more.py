from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0009_paymenttransaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='advertisement',
            name='clicks_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='advertisement',
            name='impressions_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
