from django.core.exceptions import ObjectDoesNotExist
from selenium.common.exceptions import NoSuchElementException

from workflow.models import Rater, Workflow, Item, Answer
from workflow.choices import WORKFLOW_TYPE_CHOICES
from tests.selenium.base import SeleniumBaseRemoteTest
from workflow.alerts import NOT_ALL_REQUIRED_FIELDS_ALERTS, PREDICTION_QUESTIONS_ALERTS, INVALID_USER_ALERTS, \
    NOT_SIGNED_IN_USER_WORKFLOW_ALERTS
from .utils import send_predict_keys

WORKFLOW_NAME = 'workflow1'
WORKFLOW_TYPE = WORKFLOW_TYPE_CHOICES.EVIDENCE_URL_INPUT_WORKFLOW

WORKFLOW_DONE_ALERT_XPATH = '//div[@class="alert alert-success alert-dismissible fade show"]'
WARNING_ALERTS_XPATH = '//div[@class="alert alert-warning alert-dismissible fade show"]'

SIGN_IN_TEXT = ['Sign in']
SIGN_IN_XPATH = '//h1[@class="mt-2"]'


class WorkflowRegisterTest(SeleniumBaseRemoteTest):

    def test_answer(self):
        item = Item.objects.create(url='www.test.com', category='test_category', is_active=True)
        for x in range(1, 5):
            workflow = Workflow.objects.create(
                api_id=x,
                name=WORKFLOW_NAME,
                instruction=x,
                judgment=x,
                prediction=x,
                type=WORKFLOW_TYPE)
        rater = Rater.objects.create(
            email='test1@test.com',
            api_id='1',
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)

        selenium = self.selenium
        selenium.get(self.live_server_url)

        session = self.client.session
        session['rater_id'] = '1'
        session.save()
        selenium.add_cookie({'name': 'sessionid', 'value': session._SessionBase__session_key,
                             'secure': False, 'path': '/'})
        selenium.get(f'{self.live_server_url}/workflow_form')

        rater_answer_evidence = selenium.find_element_by_id('id_id_rater_answer_evidence_0_1')
        rater_answer_evidence_url = selenium.find_element_by_id('id_evidence_url')

        rater_answer_judgment = selenium.find_element_by_id('id_id_rater_answer_judgment_0_1')
        rater_answer_predict_a = selenium.find_element_by_id('id_rater_answer_predict_a')
        rater_answer_predict_b = selenium.find_element_by_id('id_rater_answer_predict_b')
        rater_answer_predict_c = selenium.find_element_by_id('id_rater_answer_predict_c')

        submit = selenium.find_element_by_id('submit')

        rater_answer_evidence.click()
        rater_answer_judgment.click()
        rater_answer_evidence_url.send_keys('https://test.com')
        send_predict_keys(
            predict_a=rater_answer_predict_a,
            predict_b=rater_answer_predict_b,
            predict_c=rater_answer_predict_c,
            key_a=20,
            key_b=30,
            key_c=50)

        submit.click()

        self.assertEqual(Answer.objects.all().count(), 1)

        answer = Answer.objects.get(rater=rater, item=item, workflow=workflow)
        self.assertEqual(answer.rater_answer_predict_a, '20')
        self.assertEqual(answer.rater_answer_predict_b, '30')
        self.assertEqual(answer.rater_answer_predict_c, '50')
        self.assertEqual(answer.rater.api_id, '1')
        self.assertEqual(answer.item, item)
        self.assertEqual(answer.rater_answer_judgment, 'True')
        self.assertEqual(answer.evidence_url, 'https://test.com')


class WorkflowWithoutEvidenceTest(SeleniumBaseRemoteTest):

    def test_answer(self):
        Item.objects.create(url='www.test.com', category='test_category', is_active=True)
        for x in range(2, 6):
            workflow = Workflow.objects.create(
                api_id=x,
                name=WORKFLOW_NAME,
                instruction=x,
                judgment=x,
                prediction=x,
                type=WORKFLOW_TYPE)
        Rater.objects.create(
            email='test2@test.com',
            api_id='2',
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)

        selenium = self.selenium
        selenium.get(self.live_server_url)

        session = self.client.session
        session['rater_id'] = '2'
        session.save()
        selenium.add_cookie({'name': 'sessionid', 'value': session._SessionBase__session_key,
                             'secure': False, 'path': '/'})
        selenium.get(f'{self.live_server_url}/workflow_form')

        rater_answer_evidence = selenium.find_element_by_id('id_id_rater_answer_evidence_0_1')
        rater_answer_evidence_url = selenium.find_element_by_id('id_evidence_url')

        rater_answer_judgment = selenium.find_element_by_id('id_id_rater_answer_judgment_0_1')
        rater_answer_predict_a = selenium.find_element_by_id('id_rater_answer_predict_a')
        rater_answer_predict_b = selenium.find_element_by_id('id_rater_answer_predict_b')
        rater_answer_predict_c = selenium.find_element_by_id('id_rater_answer_predict_c')

        submit = selenium.find_element_by_id('submit')

        rater_answer_judgment.click()
        rater_answer_evidence_url.send_keys('https://test.com')
        rater_answer_predict_a.send_keys('20')
        rater_answer_predict_b.send_keys('30')
        rater_answer_predict_c.send_keys('50')
        submit.click()
        alerts = [alert.text.replace('\n×', '') for alert in selenium.find_elements_by_xpath(WARNING_ALERTS_XPATH)]
        self.assertEqual(alerts, NOT_ALL_REQUIRED_FIELDS_ALERTS)
        self.assertEqual(Answer.objects.all().count(), 0)


class WorkflowWithoutJudgmentTest(SeleniumBaseRemoteTest):

    def test_answer(self):
        Item.objects.create(url='www.test.com', category='test_category', is_active=True)
        workflow = None
        for x in range(2, 6):
            workflow = Workflow.objects.create(
                api_id=x,
                name=WORKFLOW_NAME,
                instruction=x,
                judgment=x,
                prediction=x,
                type=WORKFLOW_TYPE)
        Rater.objects.create(
            email='test2@test.com',
            api_id='300',
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)

        selenium = self.selenium
        selenium.get(self.live_server_url)

        session = self.client.session
        session['rater_id'] = '300'
        session.save()
        selenium.add_cookie({'name': 'sessionid', 'value': session._SessionBase__session_key,
                             'secure': False, 'path': '/'})
        selenium.get(f'{self.live_server_url}/workflow_form')

        rater_answer_evidence = selenium.find_element_by_id('id_id_rater_answer_evidence_0_1')
        rater_answer_evidence_url = selenium.find_element_by_id('id_evidence_url')

        rater_answer_judgment = selenium.find_element_by_id('id_id_rater_answer_judgment_0_1')
        rater_answer_predict_a = selenium.find_element_by_id('id_rater_answer_predict_a')
        rater_answer_predict_b = selenium.find_element_by_id('id_rater_answer_predict_b')
        rater_answer_predict_c = selenium.find_element_by_id('id_rater_answer_predict_c')

        submit = selenium.find_element_by_id('submit')

        rater_answer_evidence.click()
        rater_answer_evidence_url.send_keys('https://test.com')
        send_predict_keys(
            predict_a=rater_answer_predict_a,
            predict_b=rater_answer_predict_b,
            predict_c=rater_answer_predict_c,
            key_a=20,
            key_b=30,
            key_c=50)

        submit.click()
        alerts = [alert.text.replace('\n×', '') for alert in selenium.find_elements_by_xpath(WARNING_ALERTS_XPATH)]
        self.assertEqual(alerts, NOT_ALL_REQUIRED_FIELDS_ALERTS)
        self.assertEqual(Answer.objects.all().count(), 0)


class WorkflowWithoutPredictionTest(SeleniumBaseRemoteTest):

    def test_answer(self):
        Item.objects.create(url='www.test.com', category='test_category', is_active=True)
        workflow = None
        for x in range(2, 6):
            workflow = Workflow.objects.create(
                api_id=x,
                name=WORKFLOW_NAME,
                instruction=x,
                judgment=x,
                prediction=x,
                type=WORKFLOW_TYPE)
        Rater.objects.create(
            email='test@test.com',
            api_id='2',
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)

        selenium = self.selenium
        selenium.get(self.live_server_url)

        session = self.client.session
        session['rater_id'] = '2'
        session.save()
        selenium.add_cookie({'name': 'sessionid', 'value': session._SessionBase__session_key,
                             'secure': False, 'path': '/'})
        selenium.get(f'{self.live_server_url}/workflow_form')

        rater_answer_evidence = selenium.find_element_by_id('id_id_rater_answer_evidence_0_1')
        rater_answer_evidence_url = selenium.find_element_by_id('id_evidence_url')

        rater_answer_judgment = selenium.find_element_by_id('id_id_rater_answer_judgment_0_1')
        rater_answer_predict_a = selenium.find_element_by_id('id_rater_answer_predict_a')
        rater_answer_predict_b = selenium.find_element_by_id('id_rater_answer_predict_b')
        rater_answer_predict_c = selenium.find_element_by_id('id_rater_answer_predict_c')

        submit = selenium.find_element_by_id('submit')

        rater_answer_judgment.click()
        rater_answer_evidence.click()
        rater_answer_evidence_url.send_keys('https://test.com')

        submit.click()

        self.assertEqual(Answer.objects.all().count(), 0)


class WorkflowWithInvalidSumPredictionTest(SeleniumBaseRemoteTest):

    def test_answer(self):
        Item.objects.create(url='www.test.com', category='test_category', is_active=True)
        workflow = None
        for x in range(2, 6):
            workflow = Workflow.objects.create(
                api_id=x,
                name=WORKFLOW_NAME,
                instruction=x,
                judgment=x,
                prediction=x,
                type=WORKFLOW_TYPE)
        Rater.objects.create(
            email='test@test.com',
            api_id='2',
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)

        selenium = self.selenium
        selenium.get(self.live_server_url)

        session = self.client.session
        session['rater_id'] = '2'
        session.save()
        selenium.add_cookie({'name': 'sessionid', 'value': session._SessionBase__session_key,
                             'secure': False, 'path': '/'})
        selenium.get(f'{self.live_server_url}/workflow_form')

        rater_answer_evidence = selenium.find_element_by_id('id_id_rater_answer_evidence_0_1')
        rater_answer_evidence_url = selenium.find_element_by_id('id_evidence_url')

        rater_answer_judgment = selenium.find_element_by_id('id_id_rater_answer_judgment_0_1')
        rater_answer_predict_a = selenium.find_element_by_id('id_rater_answer_predict_a')
        rater_answer_predict_b = selenium.find_element_by_id('id_rater_answer_predict_b')
        rater_answer_predict_c = selenium.find_element_by_id('id_rater_answer_predict_c')

        submit = selenium.find_element_by_id('submit')

        rater_answer_judgment.click()
        rater_answer_evidence.click()
        rater_answer_evidence_url.send_keys('https://test.com')
        send_predict_keys(
            predict_a=rater_answer_predict_a,
            predict_b=rater_answer_predict_b,
            predict_c=rater_answer_predict_c,
            key_a=10,
            key_b=10,
            key_c=10)

        submit.click()
        alerts = [alert.text.replace('\n×', '') for alert in selenium.find_elements_by_xpath(WARNING_ALERTS_XPATH)]
        self.assertEqual(alerts, PREDICTION_QUESTIONS_ALERTS)
        self.assertEqual(Answer.objects.all().count(), 0)


class WorkflowWithInvalidUserWorkflowTest(SeleniumBaseRemoteTest):

    def test_answer(self):
        item = Item.objects.create(url='www.test.com', category='test_category', is_active=True)
        workflow = None
        for x in range(1, 5):
            workflow = Workflow.objects.create(
                api_id=x,
                name=WORKFLOW_NAME,
                instruction=x,
                judgment=x,
                prediction=x,
                type=WORKFLOW_TYPE)
        rater = Rater.objects.create(
            email='test12@test.com',
            api_id='test_judgment12',
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)

        selenium = self.selenium
        selenium.get(self.live_server_url)

        session = self.client.session
        session['rater_id'] = 'invalid_user'
        session.save()
        selenium.add_cookie({'name': 'sessionid', 'value': session._SessionBase__session_key,
                             'secure': False, 'path': '/'})
        selenium.get(f'{self.live_server_url}/workflow_form')
        alerts = [alert.text.replace('\n×', '') for alert in selenium.find_elements_by_xpath(WARNING_ALERTS_XPATH)]
        self.assertEqual(alerts, INVALID_USER_ALERTS)
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
            Answer.objects.get(rater=rater, item=item, workflow=workflow)
        self.assertEqual(Answer.objects.all().count(), 0)


class WorkflowWithoutUserInSessionWorkflowTest(SeleniumBaseRemoteTest):

    def test_answer(self):
        item = Item.objects.create(url='www.test.com', category='test_category', is_active=True)
        workflow = None
        for x in range(1, 5):
            workflow = Workflow.objects.create(
                api_id=x,
                name=WORKFLOW_NAME,
                instruction=x,
                judgment=x,
                prediction=x,
                type=WORKFLOW_TYPE)
        rater = Rater.objects.create(
            email='test13@test.com',
            api_id='test_judgment13',
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)

        selenium = self.selenium
        selenium.get(self.live_server_url)

        session = self.client.session
        session.save()
        selenium.add_cookie({'name': 'sessionid', 'value': session._SessionBase__session_key,
                             'secure': False, 'path': '/'})
        selenium.get(f'{self.live_server_url}/workflow_form')
        alerts = [alert.text.replace('\n×', '') for alert in selenium.find_elements_by_xpath(WARNING_ALERTS_XPATH)]
        self.assertEqual(alerts, NOT_SIGNED_IN_USER_WORKFLOW_ALERTS)
        sign_in_text = [sign_in.text for sign_in in selenium.find_elements_by_xpath(SIGN_IN_XPATH)]
        self.assertEqual(sign_in_text, SIGN_IN_TEXT)
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

        with self.assertRaises(ObjectDoesNotExist):
            Answer.objects.get(rater=rater, item=item, workflow=workflow)
        self.assertEqual(Answer.objects.all().count(), 0)
