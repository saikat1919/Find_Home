from django.db import migrations

def create_profiles_for_superusers(apps, schema_editor):
    User = apps.get_model("auth", "User")  # get the User model
    UserProfile = apps.get_model("home", "UserProfile")  # your custom profile model

    for user in User.objects.filter(is_superuser=True):
        if not UserProfile.objects.filter(user=user).exists():
            UserProfile.objects.create(user=user)
            print(f"✅ Created UserProfile for superuser: {user.username}")
        else:
            print(f"ℹ️ UserProfile already exists for: {user.username}")

class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_auto_20250910_2220'),
    ]

    operations = [
        migrations.RunPython(create_profiles_for_superusers),
    ]
