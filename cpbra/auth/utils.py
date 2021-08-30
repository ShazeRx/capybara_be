from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.urls import reverse


class MailSenderUtil:
    @staticmethod
    def send_email(request, user_data, tokens: dict):
        current_site = get_current_site(request).domain
        relative_link = reverse('email-verify')
        abs_url = f'http://{current_site}{relative_link}?token={tokens["access"]}'
        email_body = f'Hi {user_data["username"]}. Use link below to verify your email.\n\n{abs_url}'
        email = EmailMessage(subject='Verify your email', body=email_body, to=[user_data['email']])
        email.send()
