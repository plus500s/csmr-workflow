from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from selenium.common.exceptions import NoSuchElementException

from workflow.models import Rater, Workflow, Item, Answer
from tests.selenium.base import SeleniumBaseRemoteTest

WORKFLOW_NAME = 'workflow2'

NOT_ALL_REQUIRED_FIELDS_ALERTS = ['Not all required fields have been entered.',
                                  'Please, try again.']
WORKFLOW_DONE_ALERTS = ['Workflow done']
PREDICTION_QUESTIONS_ALERTS = ['Please, enter valid percentage for Prediction question.',
                               'Sum of A, B and C answers should be 100.Please, try again.']
WORKFLOW_DONE_ALERT_XPATH = '//div[@class="alert alert-success"]'
WARNING_ALERTS_XPATH = '//div[@class="alert alert-warning"]'
INVALID_WORKFLOW_ALERTS = ['Got no Workflow for this User']
INVALID_USER_ALERTS = ['Invalid User, please, try again']
NOT_SIGNED_IN_USER_ALERTS = ['You are not signed in our system!',
                             'Please, sign in to have an access to workflow page!']
SIGN_IN_TEXT = ['Sign in']
SIGN_IN_XPATH = '//h1[@class="mt-2"]'


class JudgmentRegisterTest(SeleniumBaseRemoteTest):

    def test_answer(self):
        item = Item.objects.create(id=100, api_id=100, url='www.test.com', category='test_category')
        workflow = None
        for x in range(1, 5):
            workflow = Workflow.objects.create(
                api_id=x,
                name=WORKFLOW_NAME,
                instruction=x,
                judgment=x,
                prediction=x)
        rater = Rater.objects.create(
            email='test_judgment1@test.com',
            api_id='test_judgment1',
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)
        previous_rater = Rater.objects.create(
            email='test_judgment_previous1@test.com',
            api_id='test_judgment_previous1',
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)
        answer_start = datetime.now()
        answer_end = datetime.now()
        Answer.objects.create(
            id=100,
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
        session['rater_id'] = 'test_judgment1'
        session.save()
        selenium.add_cookie({'name': 'sessionid', 'value': session._SessionBase__session_key,
                             'secure': False, 'path': '/'})
        selenium.get(f'{self.live_server_url}/workflow_form')
        rater_answer_judgment = selenium.find_element_by_id('id_id_rater_answer_judgment_0_1')
        rater_answer_evidence = selenium.find_element_by_id('id_id_evidence_url_0_1')
        rater_answer_predict_a = selenium.find_element_by_id('id_rater_answer_predict_a')
        rater_answer_predict_b = selenium.find_element_by_id('id_rater_answer_predict_b')
        rater_answer_predict_c = selenium.find_element_by_id('id_rater_answer_predict_c')

        submit = selenium.find_element_by_id('submit')

        rater_answer_evidence.click()
        rater_answer_judgment.click()

        rater_answer_predict_a.send_keys('10')
        rater_answer_predict_b.send_keys('30')
        rater_answer_predict_c.send_keys('60')

        submit.click()
        alerts = [alert.text for alert in selenium.find_elements_by_xpath(WORKFLOW_DONE_ALERT_XPATH)]
        self.assertEqual(alerts, WORKFLOW_DONE_ALERTS)
        answer = Answer.objects.get(rater=rater, item=item, workflow=workflow)
        self.assertEqual(Answer.objects.all().count(), 2)
        self.assertEqual(answer.rater_answer_predict_a, '10')
        self.assertEqual(answer.rater_answer_predict_b, '30')
        self.assertEqual(answer.rater_answer_predict_c, '60')
        self.assertEqual(answer.rater.api_id, 'test_judgment1')
        self.assertEqual(answer.item.id, 100)
        self.assertEqual(answer.rater_answer_judgment, 'False')
        self.assertEqual(answer.evidence_url, 'https//test.evidence.com')


class JudgmentNoneEvidenceChoiceTest(SeleniumBaseRemoteTest):
    def test_answer(self):
        item = Item.objects.create(id=5, api_id=5, url='www.test.com', category='test_category')
        workflow = None
        for x in range(1, 5):
            workflow = Workflow.objects.create(
                api_id=x,
                name=WORKFLOW_NAME,
                instruction=x,
                judgment=x,
                prediction=x)
        rater = Rater.objects.create(
            email='test5@test.com',
            api_id='test_judgment2',
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)
        previous_rater = Rater.objects.create(
            email='test_judgment_previous2@test.com',
            api_id='test_judgment_previous2',
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)
        answer_start = datetime.now()
        answer_end = datetime.now()
        Answer.objects.create(
            id=5,
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
        session['rater_id'] = 'test_judgment2'
        session.save()
        selenium.add_cookie({'name': 'sessionid', 'value': session._SessionBase__session_key,
                             'secure': False, 'path': '/'})
        selenium.get(f'{self.live_server_url}/workflow_form')

        rater_answer_judgment = selenium.find_element_by_id('id_id_rater_answer_judgment_0_1')
        rater_answer_evidence = selenium.find_element_by_id('id_id_evidence_url_0_2')

        rater_answer_predict_a = selenium.find_element_by_id('id_rater_answer_predict_a')
        rater_answer_predict_b = selenium.find_element_by_id('id_rater_answer_predict_b')
        rater_answer_predict_c = selenium.find_element_by_id('id_rater_answer_predict_c')

        submit = selenium.find_element_by_id('submit')

        rater_answer_judgment.click()
        rater_answer_evidence.click()
        rater_answer_predict_a.send_keys('10')
        rater_answer_predict_b.send_keys('20')
        rater_answer_predict_c.send_keys('70')

        submit.click()
        alerts = [alert.text for alert in selenium.find_elements_by_xpath(WORKFLOW_DONE_ALERT_XPATH)]
        self.assertEqual(alerts, WORKFLOW_DONE_ALERTS)
        answer = Answer.objects.get(rater=rater, item=item, workflow=workflow)
        self.assertEqual(Answer.objects.all().count(), 2)
        self.assertEqual(answer.rater_answer_predict_a, '10')
        self.assertEqual(answer.rater_answer_predict_b, '20')
        self.assertEqual(answer.rater_answer_predict_c, '70')
        self.assertEqual(answer.rater.api_id, 'test_judgment2')
        self.assertEqual(answer.item.id, 5)
        self.assertEqual(answer.rater_answer_judgment, 'False')
        self.assertEqual(answer.evidence_url, None)


class JudgmentWithAlreadyDoneWorkflowTest(SeleniumBaseRemoteTest):

    def test_answer(self):
        item = Item.objects.create(id=9, api_id=9, url='www.test.com', category='test_category')
        workflow = None
        for x in range(1, 5):
            workflow = Workflow.objects.create(
                api_id=x,
                name=WORKFLOW_NAME,
                instruction=x,
                judgment=x,
                prediction=x)
        rater = Rater.objects.create(
            email='test9@test.com',
            api_id='test_judgment3',
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)
        answer_start = datetime.now()
        answer_end = datetime.now()
        answer = Answer.objects.create(
            id=9,
            rater=rater,
            item=item,
            workflow=workflow,
            answer_start=answer_start,
            answer_end=answer_end,
            evidence_url='https//test.evidence.com'
        )

        selenium = self.selenium
        selenium.get(self.live_server_url)

        session = self.client.session
        session['rater_id'] = 'test_judgment3'
        session.save()
        selenium.add_cookie({'name': 'sessionid', 'value': session._SessionBase__session_key,
                             'secure': False, 'path': '/'})
        selenium.get(f'{self.live_server_url}/workflow_form')
        alerts = [alert.text for alert in selenium.find_elements_by_xpath(WORKFLOW_DONE_ALERT_XPATH)]
        self.assertEqual(alerts, WORKFLOW_DONE_ALERTS)
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


class JudgmentWithoutEvidenceTest(SeleniumBaseRemoteTest):
    def test_answer(self):
        item = Item.objects.create(id=5, api_id=5, url='www.test.com', category='test_category')
        workflow = None
        for x in range(1, 5):
            workflow = Workflow.objects.create(
                api_id=x,
                name=WORKFLOW_NAME,
                instruction=x,
                judgment=x,
                prediction=x)
        rater = Rater.objects.create(
            email='test5@test.com',
            api_id='test_judgment4',
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)
        previous_rater = Rater.objects.create(
            email='test_judgment_previous4@test.com',
            api_id='test_judgment_previous4',
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)
        answer_start = datetime.now()
        answer_end = datetime.now()
        Answer.objects.create(
            id=5,
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
        session['rater_id'] = 'test_judgment4'
        session.save()
        selenium.add_cookie({'name': 'sessionid', 'value': session._SessionBase__session_key,
                             'secure': False, 'path': '/'})
        selenium.get(f'{self.live_server_url}/workflow_form')

        rater_answer_judgment = selenium.find_element_by_id('id_id_rater_answer_judgment_0_1')

        rater_answer_predict_a = selenium.find_element_by_id('id_rater_answer_predict_a')
        rater_answer_predict_b = selenium.find_element_by_id('id_rater_answer_predict_b')
        rater_answer_predict_c = selenium.find_element_by_id('id_rater_answer_predict_c')

        submit = selenium.find_element_by_id('submit')

        rater_answer_judgment.click()
        rater_answer_predict_a.send_keys('10')
        rater_answer_predict_b.send_keys('20')
        rater_answer_predict_c.send_keys('60')

        submit.click()
        alerts = [alert.text for alert in selenium.find_elements_by_xpath(WARNING_ALERTS_XPATH)]
        self.assertEqual(alerts, NOT_ALL_REQUIRED_FIELDS_ALERTS)
        with self.assertRaises(ObjectDoesNotExist):
            Answer.objects.get(rater=rater, item=item, workflow=workflow)
        self.assertEqual(Answer.objects.all().count(), 1)


class JudgmentWithoutJudgmentTest(SeleniumBaseRemoteTest):
    def test_answer(self):
        item = Item.objects.create(id=6, api_id=6, url='www.test.com', category='test_category')
        workflow = None
        for x in range(1, 5):
            workflow = Workflow.objects.create(
                api_id=x,
                name=WORKFLOW_NAME,
                instruction=x,
                judgment=x,
                prediction=x)
        rater = Rater.objects.create(
            email='test6@test.com',
            api_id='test_judgment5',
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)
        previous_rater = Rater.objects.create(
            email='test_judgment_previous5@test.com',
            api_id='test_judgment_previous5',
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)
        answer_start = datetime.now()
        answer_end = datetime.now()
        Answer.objects.create(
            id=6,
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
        session['rater_id'] = 'test_judgment5'
        session.save()
        selenium.add_cookie({'name': 'sessionid', 'value': session._SessionBase__session_key,
                             'secure': False, 'path': '/'})
        selenium.get(f'{self.live_server_url}/workflow_form')

        rater_answer_evidence = selenium.find_element_by_id('id_id_evidence_url_0_1')
        rater_answer_judgment = selenium.find_element_by_id('id_id_rater_answer_judgment_0_1')

        rater_answer_predict_a = selenium.find_element_by_id('id_rater_answer_predict_a')
        rater_answer_predict_b = selenium.find_element_by_id('id_rater_answer_predict_b')
        rater_answer_predict_c = selenium.find_element_by_id('id_rater_answer_predict_c')

        submit = selenium.find_element_by_id('submit')

        rater_answer_evidence.click()
        rater_answer_predict_a.send_keys('10')
        rater_answer_predict_b.send_keys('20')
        rater_answer_predict_c.send_keys('60')

        submit.click()
        alerts = [alert.text for alert in selenium.find_elements_by_xpath(WARNING_ALERTS_XPATH)]
        self.assertEqual(alerts, NOT_ALL_REQUIRED_FIELDS_ALERTS)
        with self.assertRaises(ObjectDoesNotExist):
            Answer.objects.get(rater=rater, item=item, workflow=workflow)
        self.assertEqual(Answer.objects.all().count(), 1)


class JudgmentWithoutPredictionTest(SeleniumBaseRemoteTest):
    def test_answer(self):
        item = Item.objects.create(id=7, api_id=7, url='www.test.com', category='test_category')
        workflow = None
        for x in range(1, 5):
            workflow = Workflow.objects.create(
                api_id=x,
                name=WORKFLOW_NAME,
                instruction=x,
                judgment=x,
                prediction=x)
        rater = Rater.objects.create(
            email='test7@test.com',
            api_id='test_judgment7',
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)
        previous_rater = Rater.objects.create(
            email='test_judgment_previous7@test.com',
            api_id='test_judgment_previous7',
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)
        answer_start = datetime.now()
        answer_end = datetime.now()
        Answer.objects.create(
            id=7,
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
        session['rater_id'] = 'test_judgment7'
        session.save()
        selenium.add_cookie({'name': 'sessionid', 'value': session._SessionBase__session_key,
                             'secure': False, 'path': '/'})
        selenium.get(f'{self.live_server_url}/workflow_form')

        rater_answer_evidence = selenium.find_element_by_id('id_id_evidence_url_0_1')
        rater_answer_judgment = selenium.find_element_by_id('id_id_rater_answer_judgment_0_1')

        rater_answer_predict_a = selenium.find_element_by_id('id_rater_answer_predict_a')
        rater_answer_predict_b = selenium.find_element_by_id('id_rater_answer_predict_b')
        rater_answer_predict_c = selenium.find_element_by_id('id_rater_answer_predict_c')

        submit = selenium.find_element_by_id('submit')

        rater_answer_evidence.click()
        rater_answer_judgment.click()

        submit.click()

        with self.assertRaises(ObjectDoesNotExist):
            Answer.objects.get(rater=rater, item=item, workflow=workflow)
        self.assertEqual(Answer.objects.all().count(), 1)


class JudgmentWithInvalidTypePredictionTest(SeleniumBaseRemoteTest):
    def test_answer(self):
        item = Item.objects.create(id=8, api_id=8, url='www.test.com', category='test_category')
        workflow = None
        for x in range(1, 5):
            workflow = Workflow.objects.create(
                api_id=x,
                name=WORKFLOW_NAME,
                instruction=x,
                judgment=x,
                prediction=x)
        rater = Rater.objects.create(
            email='test8@test.com',
            api_id='test_judgment8',
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)
        previous_rater = Rater.objects.create(
            email='test_judgment_previous8@test.com',
            api_id='test_judgment_previous8',
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)
        answer_start = datetime.now()
        answer_end = datetime.now()
        Answer.objects.create(
            id=8,
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
        session['rater_id'] = 'test_judgment8'
        session.save()
        selenium.add_cookie({'name': 'sessionid', 'value': session._SessionBase__session_key,
                             'secure': False, 'path': '/'})
        selenium.get(f'{self.live_server_url}/workflow_form')

        rater_answer_evidence = selenium.find_element_by_id('id_id_evidence_url_0_1')
        rater_answer_judgment = selenium.find_element_by_id('id_id_rater_answer_judgment_0_1')

        rater_answer_predict_a = selenium.find_element_by_id('id_rater_answer_predict_a')
        rater_answer_predict_b = selenium.find_element_by_id('id_rater_answer_predict_b')
        rater_answer_predict_c = selenium.find_element_by_id('id_rater_answer_predict_c')

        submit = selenium.find_element_by_id('submit')

        rater_answer_evidence.click()
        rater_answer_judgment.click()
        rater_answer_predict_a.send_keys('invalid_type_a')
        rater_answer_predict_b.send_keys('invalid_type_b')
        rater_answer_predict_c.send_keys('invalid_type_c')

        submit.click()

        with self.assertRaises(ObjectDoesNotExist):
            Answer.objects.get(rater=rater, item=item, workflow=workflow)
        self.assertEqual(Answer.objects.all().count(), 1)


class JudgmentWithInvalidSumPredictionTest(SeleniumBaseRemoteTest):
    def test_answer(self):
        item = Item.objects.create(id=9, api_id=9, url='www.test.com', category='test_category')
        workflow = None
        for x in range(1, 5):
            workflow = Workflow.objects.create(
                api_id=x,
                name=WORKFLOW_NAME,
                instruction=x,
                judgment=x,
                prediction=x)
        rater = Rater.objects.create(
            email='test9@test.com',
            api_id='test_judgment9',
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)
        previous_rater = Rater.objects.create(
            email='test_judgment_previous9@test.com',
            api_id='test_judgment_previous9',
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)
        answer_start = datetime.now()
        answer_end = datetime.now()
        Answer.objects.create(
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
        session['rater_id'] = 'test_judgment9'
        session.save()
        selenium.add_cookie({'name': 'sessionid', 'value': session._SessionBase__session_key,
                             'secure': False, 'path': '/'})
        selenium.get(f'{self.live_server_url}/workflow_form')

        rater_answer_evidence = selenium.find_element_by_id('id_id_evidence_url_0_1')
        rater_answer_judgment = selenium.find_element_by_id('id_id_rater_answer_judgment_0_1')

        rater_answer_predict_a = selenium.find_element_by_id('id_rater_answer_predict_a')
        rater_answer_predict_b = selenium.find_element_by_id('id_rater_answer_predict_b')
        rater_answer_predict_c = selenium.find_element_by_id('id_rater_answer_predict_c')

        submit = selenium.find_element_by_id('submit')

        rater_answer_evidence.click()
        rater_answer_judgment.click()
        rater_answer_predict_a.send_keys('100')
        rater_answer_predict_b.send_keys('100')
        rater_answer_predict_c.send_keys('100')

        submit.click()
        alerts = [alert.text for alert in selenium.find_elements_by_xpath(WARNING_ALERTS_XPATH)]
        self.assertEqual(alerts, PREDICTION_QUESTIONS_ALERTS)
        with self.assertRaises(ObjectDoesNotExist):
            Answer.objects.get(rater=rater, item=item, workflow=workflow)
        self.assertEqual(Answer.objects.all().count(), 1)


class JudgmentWithInvalidUserWorkflowTest(SeleniumBaseRemoteTest):

    def test_answer(self):
        item = Item.objects.create(id=11, api_id=11, url='www.test.com', category='test_category')
        workflow = None
        for x in range(1, 5):
            workflow = Workflow.objects.create(
                api_id=x,
                name=WORKFLOW_NAME,
                instruction=x,
                judgment=x,
                prediction=x)
        rater = Rater.objects.create(
            email='test10@test.com',
            api_id='test_judgment11',
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)
        previous_rater = Rater.objects.create(
            email='test_judgment_previous11@test.com',
            api_id='test_judgment_previous11',
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)
        answer_start = datetime.now()
        answer_end = datetime.now()
        Answer.objects.create(
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
        session['rater_id'] = 'invalid_user'
        session.save()
        selenium.add_cookie({'name': 'sessionid', 'value': session._SessionBase__session_key,
                             'secure': False, 'path': '/'})
        selenium.get(f'{self.live_server_url}/workflow_form')
        alerts = [alert.text for alert in selenium.find_elements_by_xpath(WARNING_ALERTS_XPATH)]
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
        self.assertEqual(Answer.objects.all().count(), 1)


class JudgmentWithoutUserInSessionWorkflowTest(SeleniumBaseRemoteTest):

    def test_answer(self):
        item = Item.objects.create(id=11, api_id=11, url='www.test.com', category='test_category')
        workflow = None
        for x in range(1, 5):
            workflow = Workflow.objects.create(
                api_id=x,
                name=WORKFLOW_NAME,
                instruction=x,
                judgment=x,
                prediction=x)
        rater = Rater.objects.create(
            email='test10@test.com',
            api_id='test_judgment11',
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)
        previous_rater = Rater.objects.create(
            email='test_judgment_previous12@test.com',
            api_id='test_judgment_previous13',
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)
        answer_start = datetime.now()
        answer_end = datetime.now()
        Answer.objects.create(
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
        session.save()
        selenium.add_cookie({'name': 'sessionid', 'value': session._SessionBase__session_key,
                             'secure': False, 'path': '/'})
        selenium.get(f'{self.live_server_url}/workflow_form')
        alerts = [alert.text for alert in selenium.find_elements_by_xpath(WARNING_ALERTS_XPATH)]
        self.assertEqual(alerts, NOT_SIGNED_IN_USER_ALERTS)
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
        self.assertEqual(Answer.objects.all().count(), 1)
