from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Создает суперпользователя с email admin@example.com и паролем 12345qwerty"

    def handle(self, *args, **options):
        email = "admin@example.com"
        password = "12345qwerty"

        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(f"Пользователь {email} уже существует")
            )
            return

        try:
            User.objects.create_superuser(
                username="admin", email=email, password=password
            )
            self.stdout.write(
                self.style.SUCCESS(f"Суперпользователь {email} успешно создан")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка: {str(e)}"))
