
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Create or update Render admin user"

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.environ.get("DJANGO_ADMIN_USERNAME")
        email = os.environ.get("DJANGO_ADMIN_EMAIL")
        password = os.environ.get("DJANGO_ADMIN_PASSWORD")

        if not username or not password:
            self.stdout.write("Admin environment variables not set. Skipping.")
            return

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email or "",
                "role": "admin",
                "is_staff": True,
                "is_superuser": True,
            },
        )

        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS("Render admin created."))
        else:
            self.stdout.write("Admin username already exists. No changes made.")
