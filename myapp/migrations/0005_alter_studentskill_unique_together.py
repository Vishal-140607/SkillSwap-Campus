from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_notification'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='studentskill',
            unique_together={('student', 'skill', 'skill_type')},
        ),
    ]
