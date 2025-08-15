from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Notification, UserContacts


class NotificationSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Notification.

    Преобразует объекты уведомлений в JSON и обратно.
    Включает все основные поля модели.
    """

    class Meta:
        model = Notification
        fields = ["id", "subject", "message", "is_sent"]


class UserContactsSerializer(serializers.ModelSerializer):
    """Сериализатор для контактных данных пользователя.

    Используется для создания, обновления и отображения
    контактной информации пользователя.
    """

    class Meta:
        model = UserContacts
        fields = ["email", "phone", "telegram_chat_id"]


User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации новых пользователей.

    Обрабатывает данные при регистрации:
    - username (обязательное поле)
    - password (обязательное поле, write-only)
    - email (опциональное поле)
    """

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "password", "email"]

    def create(self, validated_data):
        """Создает и возвращает нового пользователя с хешированным паролем.

        Args:
            validated_data (dict): Валидированные данные пользователя

        Returns:
            User: Созданный объект пользователя
        """
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            email=validated_data.get("email", ""),
        )
        return user


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Кастомный сериализатор для JWT токенов.

    Расширяет стандартный сериализатор, добавляя
    username в payload токена.
    """

    @classmethod
    def get_token(cls, user):
        """Создает JWT токен с дополнительными данными.

        Args:
            user (User): Объект пользователя Django

        Returns:
            Token: JWT токен с добавленным username в payload
        """
        token = super().get_token(user)
        token["username"] = user.username
        return token
