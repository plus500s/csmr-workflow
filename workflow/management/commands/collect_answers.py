from django.core.management.base import BaseCommand, CommandError
from workflow.services.mturk import MTurkConnection


class Command(BaseCommand):
    help = 'Collect Answers and Assignments on Amazon MTurk'

    def handle(self, *args, **kwargs):  # noqa
        try:
            mturk = MTurkConnection()
            hits = mturk.client.list_hits()
            all_assignments = []
            for hit in hits.get('HITs'):
                assignments = mturk.client.list_assignments_for_hit(
                    HITId=hit.get('HITId')
                ).get('Assignments')
                for assignment in assignments:
                    all_assignments.append(assignment)
            print(all_assignments)  # TODO make something with answers
        except IOError:
            raise CommandError()
