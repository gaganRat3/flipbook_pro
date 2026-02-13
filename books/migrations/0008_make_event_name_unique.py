# Generated migration for Event name uniqueness

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0007_remove_unlockrequest_payment_screenshot_and_more'),
    ]

    operations = [
        # First, let's handle any duplicate events before making name unique
        migrations.RunSQL(
            """
            UPDATE books_event 
            SET name = CONCAT(name, ' (', id, ')') 
            WHERE id NOT IN (
                SELECT min_id FROM (
                    SELECT MIN(id) as min_id 
                    FROM books_event 
                    GROUP BY LOWER(name)
                ) as subquery
            );
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        # Now make the name field unique
        migrations.AlterField(
            model_name='event',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]