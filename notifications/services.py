import requests
from django.core.exceptions import ValidationError
from django.core.mail import send_mail

from config.settings import (EMAIL_HOST_USER, TELE2_API_KEY, TELE2_SENDER_NAME,
                             TELE2_URL, TELEGRAM_BOT_TOKEN, TELEGRAM_URL)
from notifications.models import UserContacts


class NotificationService:
    """Сервис для отправки уведомлений пользователям через различные каналы связи.

    Поддерживает отправку через:
    - Email
    - SMS (через API Tele2)
    - Telegram бота

    При инициализации требует пользователя, для которого будут отправляться уведомления.
    """

    def __init__(self, user):
        """Инициализирует сервис уведомлений для конкретного пользователя.

        Args:
            user (User): Объект пользователя Django

        Raises:
            ValidationError: Если у пользователя не заполнены контактные данные
        """
        self.user = user
        try:
            self.contacts = user.contacts
        except UserContacts.DoesNotExist:
            raise ValidationError("Контакты пользователя не заполнены")

    def send_notification(self, subject, message):
        """Отправляет уведомление через доступные каналы с резервными вариантами.

        Пытается отправить уведомление последовательно через разные каналы
        по приоритету: Email -> SMS -> Telegram. Возвращает True при первой
        успешной отправке.

        Args:
            subject (str): Тема уведомления
            message (str): Текст уведомления

        Returns:
            bool: True если уведомление было успешно отправлено хотя бы одним способом

        Raises:
            Exception: Если все способы доставки не сработали (содержит текст последней ошибки)
        """
        channels = [
            ("email", self._send_email, {"subject": subject, "message": message}),
            ("sms", self._send_sms, {"message": f"{subject}\n{message}"}),
            ("telegram", self._send_telegram, {"message": f"*{subject}*\n{message}"}),
        ]

        last_error = None

        for channel_name, method, params in channels:
            try:
                if method(**params):
                    return True
            except Exception as e:
                last_error = str(e)
                continue

        if last_error:
            raise Exception(
                f"Все способы доставки не сработали. Последняя ошибка: {last_error}"
            )
        return False

    def _send_email(self, subject, message):
        """Отправляет уведомление по электронной почте.

        Args:
            subject (str): Тема письма
            message (str): Текст письма

        Returns:
            bool: True если письмо было успешно отправлено
        """
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=EMAIL_HOST_USER,
                recipient_list=[self.contacts.email],
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Ошибка отправки email: {str(e)}")

    def _send_sms(self, message):
        """Отправляет SMS сообщение через API Tele2.

        Args:
            message (str): Текст SMS сообщения

        Returns:
            bool: True если SMS было успешно отправлено,
                  False если не настроен API ключ Tele2
        """
        try:
            if not TELE2_API_KEY:
                return False

            url = TELE2_URL
            headers = {
                "Authorization": f"Bearer {TELE2_API_KEY}",
                "Content-Type": "application/json",
            }
            payload = {
                "sender": TELE2_SENDER_NAME,
                "text": message,
                "msisdn": self.contacts.phone,
            }

            response = requests.post(url, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                return True
            else:
                error_msg = response.json().get("message", "Unknown error")
                print(f"Tele2 API error: {error_msg}")

        except Exception as e:
            print(f"Ошибка отправки SMS: {str(e)}")

    def _send_telegram(self, message):
        """Отправляет уведомление в Telegram через бота.

        Args:
            message (str): Текст сообщения (поддерживается Markdown форматирование)

        Returns:
            dict or bool: Ответ API Telegram при успешной отправке,
                         False если не настроен токен бота
        """
        try:
            if not TELEGRAM_BOT_TOKEN:
                return False
            params = {
                "text": message,
                "chat_id": self.contacts.telegram_chat_id,
            }
            response = requests.post(
                f"{TELEGRAM_URL}{TELEGRAM_BOT_TOKEN}/sendMessage", params=params
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Ошибка отправки в Telegram: {str(e)}")
