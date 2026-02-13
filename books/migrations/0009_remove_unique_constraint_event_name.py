# Migration to remove unique constraint from Event name

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0008_make_event_name_unique'),
    ]

    operations = [
        # Remove unique constraint from event name
        migrations.AlterField(
            model_name='event',
            name='name',
            field=models.CharField(max_length=255),
        ),
    ]