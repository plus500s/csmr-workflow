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
                url_list = list(reader)
                affected_items_pks = []
                for url_row in url_list:
                    for url in url_row:
                        try:
                            item, created = Item.objects.get_or_create(
                                url=url
                            )
                            item.save()
                            affected_items_pks.append(item.pk)
                            if created:
                                self.stdout.write("Created new item with url %s" % url)
                        except Item.MultipleObjectsReturned:
                            self.stdout.write("In database there are clones with url %s" % url)
                            continue
                if affected_items_pks:
                    Item.objects.exclude(pk__in=affected_items_pks).update(is_active=False)
        except FileNotFoundError:
            raise CommandError('Cannot find file "%s"' % file_path)
