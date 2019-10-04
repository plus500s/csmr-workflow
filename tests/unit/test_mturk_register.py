from unittest import mock

from django.test import TestCase
from django.urls import reverse

from workflow.services.mturk import MTurkConnection
from workflow.models import Rater, Assignment, Workflow
from workflow.choices import WORKFLOW_TYPE_CHOICES

MTURK_REGISTER_URL = reverse('mturk_register')
WORKFLOW_NAME = 'workflow1'
WORKFLOW_TYPE = WORKFLOW_TYPE_CHOICES.EVIDENCE_URL_INPUT_WORKFLOW


class TestRegister(TestCase):
    new_worker_data = {
        'workerId': 'unexisted_worker',
        'hitId': 'some_hit_id',
        'assignmentId': 'some_assignment',
    }
    existed_worker_data = {
        'workerId': 'existed_worker',
        'hitId': 'some_hit_id',
        'assignmentId': 'some_assignment',
    }
    rejected_worker_data = {
        'workerId': 'rejected_worker',
        'hitId': 'some_hit_id',
        'assignmentId': 'some_assignment',
    }
    register_completed_worker_data = {
        'workerId': 'register_completed',
        'hitId': 'some_hit_id',
        'assignmentId': 'some_assignment',
    }

    def setUp(self):
        workflow = Workflow.objects.create(
            api_id=1,
            name=WORKFLOW_NAME,
            instruction=2,
            judgment=3,
            prediction=4,
            type=WORKFLOW_TYPE
        )
        existed_worker = Rater.objects.create(
            worker_id=self.existed_worker_data.get('workerId'))
        rejected_worker = Rater.objects.create(
            worker_id=self.rejected_worker_data.get('workerId'),
            rejected_state=True,
            workflow=workflow)
        register_completed_worker = Rater.objects.create(
            worker_id=self.register_completed_worker_data.get('workerId'),
            completed_register_state=True,
            workflow=workflow)

        self.payload = {
            'workflow': workflow,
            'existed_worker': existed_worker,
            'rejected_worker': rejected_worker,
            'register_completed_worker': register_completed_worker,
        }

    @mock.patch.object(MTurkConnection, '__new__')
    def test_first_post_by_new_worker(self, first_mocked):

        response = self.client.post(
            MTURK_REGISTER_URL,
            self.new_worker_data,
        )
        new_rater = Rater.objects.get(worker_id=self.new_worker_data.get('workerId'))
        assignment = Assignment.objects.get(rater=new_rater)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(assignment.is_active)
        self.assertEqual(assignment.assignment_id, self.new_worker_data.get('assignmentId'))
        self.assertEqual(new_rater.workflow, self.payload.get('workflow'))
        self.assertFalse(new_rater.rejected_state)
        self.assertFalse(new_rater.rejected_state)
        self.assertFalse(new_rater.completed_register_state)
        self.assertFalse(new_rater.completed_demographics_state)
        self.assertFalse(new_rater.completed_label)

    @mock.patch.object(MTurkConnection, '__new__')
    def test_first_post_by_existed_worker(self, first_mocked):
        response = self.client.post(
            MTURK_REGISTER_URL,
            self.existed_worker_data,
        )
        existed_worker = Rater.objects.get(worker_id=self.existed_worker_data.get('workerId'))
        assignment = Assignment.objects.get(rater=existed_worker)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.payload.get('existed_worker'), existed_worker)
        self.assertTrue(assignment.is_active)
        self.assertEqual(assignment.assignment_id, self.existed_worker_data.get('assignmentId'))
        self.assertEqual(existed_worker.workflow, self.payload.get('workflow'))
        self.assertFalse(existed_worker.rejected_state)
        self.assertFalse(existed_worker.completed_register_state)
        self.assertFalse(existed_worker.completed_demographics_state)
        self.assertFalse(existed_worker.completed_label)

    @mock.patch.object(MTurkConnection, '__new__')
    def test_first_post_by_rejected_worker(self, first_mocked):
        response = self.client.post(
            MTURK_REGISTER_URL,
            self.rejected_worker_data,
        )
        rejected_worker = Rater.objects.get(worker_id=self.rejected_worker_data.get('workerId'))
        self.assertEqual(self.payload.get('rejected_worker'), rejected_worker)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(rejected_worker.workflow, self.payload.get('workflow'))
        self.assertTrue(rejected_worker.rejected_state)
        self.assertFalse(rejected_worker.completed_register_state)
        self.assertFalse(rejected_worker.completed_demographics_state)
        self.assertFalse(rejected_worker.completed_label)

    @mock.patch.object(MTurkConnection, '__new__')
    def test_first_post_by_register_completed_worker(self, first_mocked):
        response = self.client.post(
            MTURK_REGISTER_URL,
            self.register_completed_worker_data,
        )
        register_completed_worker = Rater.objects.get(
            worker_id=self.register_completed_worker_data.get('workerId'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.payload.get('register_completed_worker'), register_completed_worker)
        self.assertEqual(register_completed_worker.workflow, self.payload.get('workflow'))
        self.assertFalse(register_completed_worker.rejected_state)
        self.assertTrue(register_completed_worker.completed_register_state)
        self.assertFalse(register_completed_worker.completed_demographics_state)
        self.assertFalse(register_completed_worker.completed_label)
