# alignment/api/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile, AuditLog
from django.dispatch import receiver
from allauth.account.signals import email_confirmed
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        AuditLog.objects.create(
            actor=instance, target=instance, action="User registered"
        )




@receiver(email_confirmed)
def send_welcome_email(request, email_address, **kwargs):
    user = email_address.user
    subject = "Welcome to Custos Labs!"


    context = {
        "username": user.username,
        "support_email": settings.DEFAULT_FROM_EMAIL,
        "site_url": "https://custoslabs.com",
    }
    text_content = render_to_string("account/email/welcome_email.txt", context)
    html_content = render_to_string("account/email/welcome_email.html", context)

    msg = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()
