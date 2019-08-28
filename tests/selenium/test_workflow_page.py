from django.contrib.auth import get_user_model

from workflow.models import Rater, Workflow, Item, Answer
from tests.selenium.base import SeleniumBaseRemoteTest


class WorkflowRegisterTest(SeleniumBaseRemoteTest):

    def test_answer(self):
        item = Item.objects.create(id=1, api_id=1, url='www.test.com', category='test_category')
        workflow = None
        for x in range(1, 5):
            workflow = Workflow.objects.create(
                api_id=x,
                name=x,
                instruction=x,
                judgment=x,
                prediction=x)
        rater = Rater.objects.create(
            email='test1@test.com',
            api_id='1',
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)
        User = get_user_model()
        temp_user = User.objects.create(username='admin')
        temp_user.set_password('password')

        selenium = self.selenium
        selenium.get(self.live_server_url)

        session = self.client.session
        session['rater_id'] = '1'
        session['item'] = 1
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
        rater_answer_predict_a.send_keys('20')
        rater_answer_predict_b.send_keys('30')
        rater_answer_predict_c.send_keys('50')

        submit.click()

        self.assertEqual(Answer.objects.all().count(), 1)

        answer = Answer.objects.get(rater=rater, item=item, workflow=workflow)
        self.assertEqual(answer.rater_answer_predict_a, '20')
        self.assertEqual(answer.rater_answer_predict_b, '30')
        self.assertEqual(answer.rater_answer_predict_c, '50')
        self.assertEqual(answer.rater.api_id, '1')
        self.assertEqual(answer.item.id, 1)
        self.assertEqual(answer.rater_answer_judgment, 'False')
        self.assertEqual(answer.evidence_url, 'https://test.com')


class WorkflowWithoutEvidenceTest(SeleniumBaseRemoteTest):

    def test_answer(self):
        Item.objects.create(id=2, api_id=2, url='www.test.com', category='test_category')
        workflow = None
        for x in range(2, 6):
            workflow = Workflow.objects.create(
                api_id=x,
                name=x,
                instruction=x,
                judgment=x,
                prediction=x)
        Rater.objects.create(
            email='test2@test.com',
            api_id='2',
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)
        User = get_user_model()
        temp_user = User.objects.create(username='adminadmin')
        temp_user.set_password('password')

        selenium = self.selenium
        selenium.get(self.live_server_url)

        session = self.client.session
        session['rater_id'] = '2'
        session['item'] = 2
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

        self.assertEqual(Answer.objects.all().count(), 0)


class WorkflowWithoutJudgmentTest(SeleniumBaseRemoteTest):

    def test_answer(self):
        Item.objects.create(id=2, api_id=2, url='www.test.com', category='test_category')
        workflow = None
        for x in range(2, 6):
            workflow = Workflow.objects.create(
                api_id=x,
                name=x,
                instruction=x,
                judgment=x,
                prediction=x)
        Rater.objects.create(
            email='test2@test.com',
            api_id='2',
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)
        User = get_user_model()
        temp_user = User.objects.create(username='adminadmin')
        temp_user.set_password('password')

        selenium = self.selenium
        selenium.get(self.live_server_url)

        session = self.client.session
        session['rater_id'] = '2'
        session['item'] = 2
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
        rater_answer_predict_a.send_keys('20')
        rater_answer_predict_b.send_keys('30')
        rater_answer_predict_c.send_keys('50')

        submit.click()

        self.assertEqual(Answer.objects.all().count(), 0)


class WorkflowWithoutPredictionTest(SeleniumBaseRemoteTest):

    def test_answer(self):
        Item.objects.create(id=2, api_id=2, url='www.test.com', category='test_category')
        workflow = None
        for x in range(2, 6):
            workflow = Workflow.objects.create(
                api_id=x,
                name=x,
                instruction=x,
                judgment=x,
                prediction=x)
        Rater.objects.create(
            email='test@test.com',
            api_id='2',
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)
        User = get_user_model()
        temp_user = User.objects.create(username='adminadmin')
        temp_user.set_password('password')

        selenium = self.selenium
        selenium.get(self.live_server_url)

        session = self.client.session
        session['rater_id'] = '2'
        session['item'] = 2
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


class WorkflowWithInvalidTypePredictionTest(SeleniumBaseRemoteTest):

    def test_answer(self):
        Item.objects.create(id=2, api_id=2, url='www.test.com', category='test_category')
        workflow = None
        for x in range(2, 6):
            workflow = Workflow.objects.create(
                api_id=x,
                name=x,
                instruction=x,
                judgment=x,
                prediction=x)
        Rater.objects.create(
            email='test@test.com',
            api_id='2',
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)
        User = get_user_model()
        temp_user = User.objects.create(username='adminadmin')
        temp_user.set_password('password')

        selenium = self.selenium
        selenium.get(self.live_server_url)

        session = self.client.session
        session['rater_id'] = '2'
        session['item'] = 2
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
        rater_answer_predict_a.send_keys('invalid_type_a')
        rater_answer_predict_b.send_keys('invalid_type_b')
        rater_answer_predict_c.send_keys('invalid_type_c')

        submit.click()

        self.assertEqual(Answer.objects.all().count(), 0)


class WorkflowWithInvalidSumPredictionTest(SeleniumBaseRemoteTest):

    def test_answer(self):
        Item.objects.create(id=2, api_id=2, url='www.test.com', category='test_category')
        workflow = None
        for x in range(2, 6):
            workflow = Workflow.objects.create(
                api_id=x,
                name=x,
                instruction=x,
                judgment=x,
                prediction=x)
        Rater.objects.create(
            email='test@test.com',
            api_id='2',
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)
        User = get_user_model()
        temp_user = User.objects.create(username='adminadmin')
        temp_user.set_password('password')

        selenium = self.selenium
        selenium.get(self.live_server_url)

        session = self.client.session
        session['rater_id'] = '2'
        session['item'] = 2
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
        rater_answer_predict_a.send_keys('100')
        rater_answer_predict_b.send_keys('100')
        rater_answer_predict_c.send_keys('100')

        submit.click()

        self.assertEqual(Answer.objects.all().count(), 0)


class WorkflowWithoutLogin(SeleniumBaseRemoteTest):
    UN_SUCCESS_ALERTS = ['You are not signed in our system!',
                         'Please, sign in to have an access to workflow page!']

    def test_answer(self):
        Item.objects.create(id=2, api_id=2, url='www.test.com', category='test_category')
        workflow = None
        for x in range(2, 6):
            workflow = Workflow.objects.create(
                api_id=x,
                name=x,
                instruction=x,
                judgment=x,
                prediction=x)
        Rater.objects.create(
            email='test@test.com',
            api_id='2',
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)
        User = get_user_model()
        temp_user = User.objects.create(username='adminadmin')
        temp_user.set_password('password')

        selenium = self.selenium
        selenium.get(self.live_server_url)

        session = self.client.session
        session.pop('rater_id', None)
        session['item'] = 2
        session.save()
        selenium.add_cookie({'name': 'sessionid', 'value': session._SessionBase__session_key,
                             'secure': False, 'path': '/'})
        selenium.get(f'{self.live_server_url}/workflow_form')

        alerts = selenium.find_elements_by_xpath('//div[@class="alert alert-success"]')
        for alert in alerts:
            self.assertTrue(alert.text in self.UN_SUCCESS_ALERTS)
