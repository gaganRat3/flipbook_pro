# Generated manually on 2026-10-03
# Changes UnlockRequestBook.price default from 500 to 300

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0015_remove_total_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unlockrequestbook',
            name='price',
            field=models.DecimalField(decimal_places=2, default=300, max_digits=10),
        ),
    ]
