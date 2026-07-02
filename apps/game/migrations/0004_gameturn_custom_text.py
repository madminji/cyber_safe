from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("game", "0003_gamescenario_interface_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="gameturn",
            name="custom_text",
            field=models.TextField(blank=True),
        ),
    ]
