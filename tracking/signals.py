from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings


@receiver(user_logged_in)
def send_login_email(sender, user, request, **kwargs):
    send_mail(
        subject='D2C Pulse Tracker - Login Notification',
        message=f'Hi {user.username},\n\nYou just logged into D2C Pulse Tracker.\n\nIf this wasn\'t you, please contact support.',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email],
        fail_silently=True,
    )