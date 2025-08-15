from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView

from notifications.models import Notification, UserContacts
from notifications.serializers import (MyTokenObtainPairSerializer,
                                       NotificationSerializer,
                                       UserContactsSerializer,
                                       UserRegistrationSerializer)
from notifications.services import NotificationService


class NotificationViewSet(ModelViewSet):
    """ViewSet для работы с уведомлениями пользователей.

    Позволяет создавать, просматривать, обновлять и удалять уведомления.
    Включает дополнительный экшен для отправки уведомлений.
    """

    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def get_queryset(self):
        """Возвращает только уведомления текущего аутентифицированного пользователя.

        Returns:
            QuerySet: Фильтрованный queryset уведомлений пользователя.
        """
        return self.queryset.filter(user=self.request.user)

    @action(detail=False, methods=["post"], url_path="send", url_name="send")
    def send(self, request):
        """Отправляет уведомление через доступные каналы связи.

        Args:
            request (Request): Объект запроса DRF, содержащий:
                - subject (str): Тема уведомления
                - message (str): Текст уведомления

        Returns:
            Response: JSON-ответ с результатом операции:
                - 200 OK: Уведомление успешно отправлено
                - 400 Bad Request: Не указана тема или сообщение
                - 500 Internal Server Error: Ошибка при отправке
        """
        user = request.user
        subject = request.data.get("subject")
        message = request.data.get("message")

        if not subject or not message:
            return Response(
                {"error": "Необходимо указать тему и сообщение"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        notification = Notification.objects.create(
            user=user, subject=subject, message=message
        )

        try:
            service = NotificationService(user)
            success = service.send_notification(subject, message)

            notification.is_sent = success
            notification.save()

            if success:
                return Response(
                    {"status": "Уведомление успешно отправлено"},
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"error": "Не удалось отправить уведомление ни одним способом"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserContactsViewSet(ModelViewSet):
    """ViewSet для управления контактными данными пользователей.

    Обеспечивает CRUD операции для контактов пользователя.
    Автоматически связывает контакты с текущим аутентифицированным пользователем.
    """

    serializer_class = UserContactsSerializer

    def get_queryset(self):
        """Возвращает только контакты текущего пользователя.

        Returns:
            QuerySet: Фильтрованный queryset контактов пользователя.
        """
        return UserContacts.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Сохраняет контакты, автоматически привязывая их к текущему пользователю.

        Args:
            serializer (UserContactsSerializer): Сериализатор с валидированными данными
        """
        serializer.save(user=self.request.user)


User = get_user_model()


class RegisterView(CreateAPIView):
    """API endpoint для регистрации новых пользователей.

    Позволяет создать нового пользователя с указанием:
    - username (обязательно)
    - password (обязательно)
    - email (опционально)
    """

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        """Создает нового пользователя в системе.

        Args:
            request (Request): Объект запроса с данными пользователя

        Returns:
            Response: JSON-ответ с результатом операции:
                - 201 Created: Пользователь успешно создан
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.create_user(
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
            email=serializer.validated_data.get("email", ""),
            last_login=timezone.now(),
        )

        headers = self.get_success_headers(serializer.data)
        return Response(
            {"status": "User created successfully"},
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class MyTokenObtainPairView(TokenObtainPairView):
    """Кастомный view для получения JWT токенов.

    Наследует стандартный TokenObtainPairView, добавляя возможность
    расширения данных в токене через MyTokenObtainPairSerializer.
    """

    serializer_class = MyTokenObtainPairSerializer
