from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

User = get_user_model()


class Notification(models.Model):
    """
    Модель для хранения и управления уведомлениями пользователей.

    Атрибуты:
        user (ForeignKey): Ссылка на пользователя, которому предназначено уведомление
        subject (CharField): Тема уведомления (макс. 255 символов)
        message (TextField): Полный текст уведомления
        is_sent (BooleanField): Флаг отправки уведомления (по умолчанию False)

    Методы:
        __str__: Возвращает строковое представление уведомления

    Мета:
        verbose_name: Человекочитаемое имя модели в единственном числе
        verbose_name_plural: Человекочитаемое имя модели во множественном числе
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
        """Строковое представление уведомления.

        Returns:
            str: Строка в формате "Тема - Пользователь"
        """
        return f"{self.subject} - {self.user}"


class UserContacts(models.Model):
    """
    Модель для хранения контактной информации пользователей.

    Содержит данные, необходимые для отправки уведомлений различными способами.
    Каждый пользователь может иметь только один набор контактов.

    Атрибуты:
        user (OneToOneField): Связь один-к-одному с пользователем
        email (EmailField): Адрес электронной почты
        phone (CharField): Номер телефона с валидацией формата
        telegram_chat_id (CharField): Идентификатор чата в Telegram

    Методы:
        __str__: Строковое представление контактов
        clean: Валидация полей модели перед сохранением
        save: Переопределение сохранения с автоматической валидацией

    Мета:
        verbose_name: Человекочитаемое имя модели
        verbose_name_plural: Человекочитаемое имя модели во множественном числе
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="contacts",
    )
    email = models.EmailField(
        verbose_name="Email адрес",
    )
    phone = models.CharField(
        max_length=12,
        verbose_name="Телефонный номер",
        validators=[
            RegexValidator(
                regex=r"^\+?\d{10,12}$",
                message="Номер телефона должен быть в формате: '+79991234567' или '89991234567'",
            )
        ],
    )
    telegram_chat_id = models.CharField(
        max_length=20,
        verbose_name="Telegram Chat ID",
    )

    class Meta:
        verbose_name = "Контакты пользователя"
        verbose_name_plural = "Контакты пользователей"

    def __str__(self):
        """Строковое представление контактов пользователя.

        Returns:
            str: Строка в формате "Контакты пользователя: {username}"
        """
        return f"Контакты пользователя: {self.user}"

    def clean(self):
        """
        Проверяет обязательные поля перед сохранением.

        Raises:
            ValidationError: Если отсутствует обязательное поле
        """

        if not self.email:
            raise ValidationError(
                "Необходимо указать Email для получения уведомлений по почте"
            )

        if not self.phone:
            raise ValidationError(
                "Необходимо указать номер телефона для получения уведомлений по SMS"
            )

        if not self.telegram_chat_id:
            raise ValidationError(
                "Необходимо указать TelegramID для получения уведомлений в Telegram"
            )

    def save(self, *args, **kwargs):
        """
        Переопределяет стандартное сохранение с обязательной валидацией.

        Args:
            *args: Аргументы родительского метода
            **kwargs: Именованные аргументы родительского метода

        Raises:
            ValidationError: Если данные не прошли валидацию
        """
        self.full_clean()
        super().save(*args, **kwargs)
