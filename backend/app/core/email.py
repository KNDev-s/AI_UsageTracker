from dataclasses import dataclass
from email.message import EmailMessage
import logging
import smtplib

from app.core.config import get_settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SentEmail:
    to_email: str
    subject: str
    body_text: str


class EmailService:
    """Transactional email dispatcher (SMTP / Mailpit in dev, memory sink in tests)."""

    def __init__(self) -> None:
        self.outbox: list[SentEmail] = []

    def clear_outbox(self) -> None:
        self.outbox.clear()

    def send_email(self, *, to_email: str, subject: str, body_text: str) -> None:
        settings = get_settings()
        record = SentEmail(to_email=to_email, subject=subject, body_text=body_text)

        if settings.app_env == "testing":
            self.outbox.append(record)
            return

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = settings.smtp_from
        msg["To"] = to_email
        msg.set_content(body_text)

        try:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
                if settings.smtp_use_tls:
                    smtp.starttls()
                if settings.smtp_user and settings.smtp_password:
                    smtp.login(settings.smtp_user, settings.smtp_password)
                smtp.send_message(msg)
        except OSError as exc:
            logger.warning("SMTP dispatch failed (%s); storing in fallback log only.", exc)
            if settings.app_env == "development":
                self.outbox.append(record)

    def send_verification_email(self, *, to_email: str, token: str) -> None:
        settings = get_settings()
        verify_url = f"{settings.app_base_url.rstrip('/')}/verify-email?token={token}"
        self.send_email(
            to_email=to_email,
            subject="AI Usage Tracker — Verifique seu e-mail",
            body_text=(
                "Bem-vindo ao AI Usage Tracker!\n\n"
                "Para confirmar seu e-mail, acesse o link abaixo:\n"
                f"{verify_url}\n\n"
                "Se você não criou esta conta, ignore esta mensagem."
            ),
        )

    def send_password_reset_email(self, *, to_email: str, token: str) -> None:
        settings = get_settings()
        reset_url = f"{settings.app_base_url.rstrip('/')}/reset-password?token={token}"
        self.send_email(
            to_email=to_email,
            subject="AI Usage Tracker — Redefinição de senha",
            body_text=(
                "Recebemos uma solicitação para redefinir sua senha.\n\n"
                "Acesse o link abaixo para escolher uma nova senha (válido por 1 hora):\n"
                f"{reset_url}\n\n"
                "Se você não solicitou, ignore esta mensagem."
            ),
        )


email_service = EmailService()

