import json

from django.core.management.base import BaseCommand, CommandError

from workflow.models import Workflow


class Command(BaseCommand):
    help = 'Update Workflow instances with information from json file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='path to json file')

    def handle(self, *args, **kwargs):  # noqa too-many-branches
        file_path = kwargs['file_path']
        try:
            with open(file_path, 'r') as f:
                workflow_updates = json.loads(f.read())
                for workflow_update in workflow_updates:
                    name = workflow_update.get('name')
                    instruction = workflow_update.get('instruction')
                    judgment = workflow_update.get('judgment')
                    prediction = workflow_update.get('prediction')
                    corroborating_question = workflow_update.get('corroborating_question')

                    try:
                        workflow_to_update = Workflow.objects.get(name=name)
                        if instruction:
                            workflow_to_update.instruction = instruction
                        if judgment:
                            workflow_to_update.judgment = judgment
                        if prediction:
                            workflow_to_update.prediction = prediction
                        if corroborating_question:
                            workflow_to_update.corroborating_question = corroborating_question
                        workflow_to_update.save()
                        self.stdout.write("Successfully updated Workflow instance with name %s" % name)
                    except Workflow.DoesNotExist:
                        self.stdout.write("There is no Workflow instance in database with name %s" % name)
                        continue
                    except Workflow.MultipleObjectsReturned:
                        self.stdout.write("There are clones Workflow instances in database with name %s" % name)
                        continue
        except FileNotFoundError:
            raise CommandError('Cannot find file "%s"' % file_path)
