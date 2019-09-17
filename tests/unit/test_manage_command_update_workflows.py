from django.core.management import call_command
from django.test import TestCase
from django.core.management.base import CommandError

from workflow.models import Workflow
from workflow.choices import WORKFLOW_TYPE_CHOICES


class UpdateWorkflowFromJsonTest(TestCase):
    def test_updated_all_workflows_from_file(self):
        Workflow.objects.create(
            api_id=1,
            name='workflow1',
            instruction='Instruction1',
            judgment='Judgment1',
            prediction='Prediction1',
            type=WORKFLOW_TYPE_CHOICES.WITHOUT_EVIDENCE_URL_WORKFLOW)
        Workflow.objects.create(
            api_id=2,
            name='workflow2',
            instruction='Instruction2',
            judgment='Judgment2',
            prediction='Prediction2',
            corroborating_question='corroborating2',
            type=WORKFLOW_TYPE_CHOICES.EVIDENCE_URL_INPUT_WORKFLOW)
        Workflow.objects.create(
            api_id=3,
            name='workflow3',
            instruction='Instruction3',
            judgment='Judgment3',
            prediction='Prediction3',
            corroborating_question='corroborating3',
            type=WORKFLOW_TYPE_CHOICES.EVIDENCE_URLS_JUDGMENT_WORKFLOW)
        self.assertEqual(Workflow.objects.all().count(), 3)
        call_command('update_workflows_from_json', 'tests/test_files/workflow_updates.json')
        for workflow_index in range(1, 4):
            workflow = Workflow.objects.get(name=f'workflow{workflow_index}')
            self.assertEqual(workflow.instruction, f'instruction{workflow_index} from file')
            self.assertEqual(workflow.judgment, f'judgment{workflow_index} from file')
            self.assertEqual(workflow.prediction, f'prediction{workflow_index} from file')
            if workflow_index == 1:
                self.assertEqual(workflow.corroborating_question, None)
            else:
                self.assertEqual(workflow.corroborating_question, f'corroborating{workflow_index} from file')
        self.assertEqual(Workflow.objects.all().count(), 3)


class UpdateWirkflowsFromUnexistedFileTest(TestCase):
    def test_unexisted_file(self):
        self.assertEqual(Workflow.objects.all().count(), 0)
        with self.assertRaises(CommandError):
            call_command('update_workflows_from_json', 'tests/test_files/unexisted_file.json')
        self.assertEqual(Workflow.objects.all().count(), 0)


class UpdateUnexistedWorkflowFromJsonTest(TestCase):
    def test_unupdated_inexisted_workflow_in_file(self):
        Workflow.objects.create(
            api_id=1,
            name='unexisted_in_file',
            instruction='Instruction1',
            judgment='Instruction1',
            prediction='Prediction1',
            type=WORKFLOW_TYPE_CHOICES.WITHOUT_EVIDENCE_URL_WORKFLOW)

        self.assertEqual(Workflow.objects.all().count(), 1)
        call_command('update_workflows_from_json', 'tests/test_files/workflow_updates.json')
        preexisted_workflow = Workflow.objects.get(name='unexisted_in_file')
        self.assertEqual(preexisted_workflow.instruction, 'Instruction1')
        self.assertEqual(preexisted_workflow.judgment, 'Instruction1')
        self.assertEqual(preexisted_workflow.prediction, 'Prediction1')
        self.assertEqual(preexisted_workflow.corroborating_question, None)
        self.assertEqual(Workflow.objects.all().count(), 1)
