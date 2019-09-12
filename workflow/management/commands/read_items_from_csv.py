import csv

from django.core.management.base import BaseCommand, CommandError

from workflow.models import Item


class Command(BaseCommand):
    help = 'Create new Item instances from csv file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='path to csv file')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        try:
            with open(file_path, 'r') as f:
                reader = csv.reader(f)
                item_list = list(reader)
                for item_row in item_list:
                    for item in item_row:
                        try:
                            Item.objects.get_or_create(
                                url=item
                            )
                        except Item.MultipleObjectsReturned:
                            self.stdout.write("In database there are clones with url %s" % item)
                            continue
        except FileNotFoundError:
            raise CommandError('Cannot find file "%s"' % file_path)
