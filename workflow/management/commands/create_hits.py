from django.core.management.base import BaseCommand, CommandError
from workflow.services.mturk import MTurkConnection


class Command(BaseCommand):
    help = 'Create HITs on Amazon MTurk'

    def handle(self, *args, **kwargs):  # noqa
        try:
            mturk = MTurkConnection()
            hits = mturk.register_hits()
            # only for debug, remove later
            for hit in hits:
                print('https://workersandbox.mturk.com/mturk/preview?groupId={}'.format(hit['HIT']['HITTypeId']))
        except IOError:
            raise CommandError()
