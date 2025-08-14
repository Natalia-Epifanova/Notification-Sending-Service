from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Notification(models.Model):
    """
    Модель для хранения уведомлений пользователей
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    subject = models.CharField(
        max_length=255,
        verbose_name="Тема уведомления",
    )
    message = models.TextField(
        verbose_name="Текст уведомления",
    )
    is_sent = models.BooleanField(
        default=False,
        verbose_name="Отправлено",
    )

    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"

    def __str__(self):
        return f"{self.subject} - {self.user}"


class UserNotificationPreference(models.Model):
    """
    Модель для хранения предпочтений пользователя по уведомлениям
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name='notification_preferences'
    )
    email_enabled = models.BooleanField(
        default=True,
        verbose_name="Email уведомления включены",
    )
    sms_enabled = models.BooleanField(
        default=False,
        verbose_name="SMS уведомления включены",
    )
    telegram_enabled = models.BooleanField(
        default=False,
        verbose_name="Telegram уведомления включены",
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name="Email адрес",
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Телефонный номер",
    )
    telegram_chat_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Telegram Chat ID",
    )

    class Meta:
        verbose_name = "Настройка уведомлений пользователя"
        verbose_name_plural = "Настройки уведомлений пользователей"

    def __str__(self):
        return f"Настройки уведомлений для {self.user}"

    def clean(self):
        """
        Валидация полей модели
        """
        from django.core.exceptions import ValidationError

        if self.email_enabled and not self.email:
            raise ValidationError(
                "Необходимо указать Email для получения уведомлений по почте"
            )

        if self.sms_enabled and not self.phone:
            raise ValidationError(
                "Необходимо указать номер телефона для получения уведомлений по SMS"
            )

        if self.telegram_enabled and not self.telegram_chat_id:
            raise ValidationError(
                "Необходимо указать TelegramID для получения уведомлений в Telegram"
            )

    def save(self, *args, **kwargs):
        """
        Переопределение метода save для автоматической валидации
        """
        self.full_clean()
        super().save(*args, **kwargs)