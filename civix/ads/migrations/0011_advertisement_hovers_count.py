from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0010_advertisement_impressions_count_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='advertisement',
            name='hovers_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
