import os
from celery.task import task
from django.core.mail import send_mail
from django.core import management

from workflow.utils import CheckFileHash


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


@task(name='update_items_and_workflows_task')
def update_items_and_workflows_task():
    """
    task for updating items and workflows from files
    """
    hash_checker = CheckFileHash()
    if hash_checker.check_hash('workflows_file'):
        management.call_command('update_workflows_from_json', 'input_files/workflow_specifications.json')
    if hash_checker.check_hash('items_file'):
        management.call_command('read_items_from_csv', 'input_files/items.csv')
