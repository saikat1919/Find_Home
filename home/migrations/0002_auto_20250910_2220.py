from django.db import migrations
import os

def create_superuser(apps, schema_editor):
    from django.contrib.auth import get_user_model
    User = get_user_model()

    username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
    password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "adminpass")
    email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@example.com")

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)
        print("Superuser created successfully.")
    else:
        print("Superuser already exists. Skipping.")

class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),  # adjust this to your last migration
    ]

    operations = [
        migrations.RunPython(create_superuser),
    ]
