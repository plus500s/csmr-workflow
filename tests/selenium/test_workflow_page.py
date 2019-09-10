from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from selenium.common.exceptions import NoSuchElementException

from workflow.models import Rater, Workflow, Item, Answer
from workflow.alerts import INVALID_WORKFLOW_ALERTS
from tests.selenium.base import SeleniumBaseRemoteTest


WARNING_ALERTS_XPATH = '//div[@class="alert alert-warning alert-dismissible fade show"]'


class WorkflowPageWithUnExistedWorkflowTest(SeleniumBaseRemoteTest):

    def test_answer(self):
        item = Item.objects.create(id=10, api_id=10, url='www.test.com', category='test_category')
        workflow = None
        for x in range(1, 5):
            workflow = Workflow.objects.create(
                api_id=x,
                name='invalid_workflow',
                instruction=x,
                judgment=x,
                prediction=x,
                type='invalid_type')
        rater = Rater.objects.create(
            email='test10@test.com',
            api_id='test_judgment10',
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)
        previous_rater = Rater.objects.create(
            email='test_judgment_previous10@test.com',
            api_id='test_judgment_previous10',
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)
        answer_start = datetime.now()
        answer_end = datetime.now()
        answer = Answer.objects.create(
            id=9,
            rater=previous_rater,
            item=item,
            workflow=workflow,
            answer_start=answer_start,
            answer_end=answer_end,
            evidence_url='https//test.evidence.com'
        )

        selenium = self.selenium
        selenium.get(self.live_server_url)

        session = self.client.session
        session['rater_id'] = 'test_judgment10'
        session.save()
        selenium.add_cookie({'name': 'sessionid', 'value': session._SessionBase__session_key,
                             'secure': False, 'path': '/'})
        selenium.get(f'{self.live_server_url}/workflow_form')
        alerts = [alert.text.replace('\n×', '') for alert in selenium.find_elements_by_xpath(WARNING_ALERTS_XPATH)]
        self.assertEqual(alerts, INVALID_WORKFLOW_ALERTS)
        with self.assertRaises(NoSuchElementException):
            selenium.find_element_by_id('id_id_rater_answer_judgment_0_1')
        with self.assertRaises(NoSuchElementException):
            selenium.find_element_by_id('id_id_evidence_url_0_1')
        with self.assertRaises(NoSuchElementException):
            selenium.find_element_by_id('id_rater_answer_predict_a')
        with self.assertRaises(NoSuchElementException):
            selenium.find_element_by_id('id_rater_answer_predict_b')
        with self.assertRaises(NoSuchElementException):
            selenium.find_element_by_id('id_rater_answer_predict_c')
        with self.assertRaises(NoSuchElementException):
            selenium.find_element_by_id('submit')

        with self.assertRaises(ObjectDoesNotExist):
            Answer.objects.exclude(id=answer.id).get(rater=rater, item=item, workflow=workflow)
        self.assertEqual(Answer.objects.all().count(), 1)

