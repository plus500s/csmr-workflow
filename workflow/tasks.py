import os
from celery.task import task
from django.core.mail import send_mail


@task(name='send_mail_task')
def send_mail_task(to, subject, body):
    """
    task for sending email
    :param to:
    :param subject:
    :param body:
    :return:
    """
    send_mail(subject=subject, message=body, recipient_list=to, from_email=os.getenv('EMAIL_HOST_USER'))
