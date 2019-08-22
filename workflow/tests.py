import sys
from importlib import import_module
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth import get_user_model
from selenium.webdriver.firefox.webdriver import WebDriver
from .models import Rater, Workflow, Item, Answer


class RaterRegisterTest(StaticLiveServerTestCase):

    def setUp(self):
        self.selenium = WebDriver(executable_path=f'{sys.path[0]}/geckodriver/geckodriver')
        super().setUp()

    def tearDown(self):
        self.selenium.quit()
        super().tearDown()

    def test_register_with_invalid_data(self):
        for x in range(1,5):
            Workflow.objects.create(api_id=x, name=x, instruction=x, judgment=x, prediction=x)

        selenium = self.selenium
        selenium.get(f'{self.live_server_url}/taskone/rater_form')

        api_id = selenium.find_element_by_id('api_id')
        age = selenium.find_element_by_id('age')
        gender = selenium.find_element_by_id('gender')
        location = selenium.find_element_by_id('location')

        submit = selenium.find_element_by_id('submit')

        api_id.send_keys('jfgdg')
        age.send_keys('15')
        gender.send_keys('m')
        location.send_keys('China')

        submit.click()

        self.assertTrue(selenium.find_element_by_id('error'))

    def test_register(self):
        for x in range(1,5):
            Workflow.objects.create(api_id=x, name=x, instruction=x, judgment=x, prediction=x)

        selenium = self.selenium
        selenium.get(f'{self.live_server_url}/taskone/rater_form')

        api_id = selenium.find_element_by_id('api_id')
        age = selenium.find_element_by_id('age')
        gender = selenium.find_element_by_id('gender')
        location = selenium.find_element_by_id('location')

        submit = selenium.find_element_by_id('submit')

        api_id.send_keys('1')
        age.send_keys('15')
        gender.send_keys('m')
        location.send_keys('China')

        submit.click()

        self.assertEqual(Rater.objects.all().count(), 1)


class WorkflowRegisterTest(StaticLiveServerTestCase):

    def setUp(self):
        self.selenium = WebDriver(
            executable_path='/Users/igormatcenko/Documents/taskOne/taskone/geckodriver/geckodriver')
        from django.conf import settings
        engine = import_module(settings.SESSION_ENGINE)
        self.session = engine.SessionStore()
        super().setUp()

    def tearDown(self):
        self.selenium.quit()
        super().tearDown()

    def test_answer_with_invalid_data(self):
        Item.objects.create(api_id=1, url='www.test.com', category='test_category')
        workflow = None
        for x in range(1, 5):
            workflow = Workflow.objects.create(api_id=x, name=x, instruction=x, judgment=x, prediction=x)
        Rater.objects.create(api_id=1, age=10, gender='m', location='Kiev', workflow=workflow)
        User = get_user_model()
        temp_user = User.objects.create(username='admin')
        temp_user.set_password('password')

        selenium = self.selenium
        selenium.get(f'{self.live_server_url}/taskone/')

        self.client.login(username='admin', password='password')

        session = self.client.session
        session['rater_id'] = 1
        session['item'] = 1
        session.save()
        selenium.add_cookie({'name': 'sessionid', 'value': session._SessionBase__session_key,
                            'secure': False, 'path': '/'})
        selenium.get(f'{self.live_server_url}/taskone/workflow_form')

        rater_answer_judgment = selenium.find_element_by_id('rater_answer_judgment')
        rater_answer_predict_a = selenium.find_element_by_id('answer_a')
        rater_answer_predict_b = selenium.find_element_by_id('answer_b')
        rater_answer_predict_c = selenium.find_element_by_id('answer_c')

        submit = selenium.find_element_by_id('submit')

        rater_answer_judgment.click()
        rater_answer_predict_a.send_keys('10')
        rater_answer_predict_b.send_keys('15')
        rater_answer_predict_c.send_keys('20')

        submit.click()

        self.assertEqual(Answer.objects.all().count(), 1)

        answer = Answer.objects.get(pk=1)
        self.assertEqual(answer.rater_answer_predict_a, '10')
        self.assertEqual(answer.rater.api_id, 1)
        self.assertEqual(answer.item.id, 1)
        self.assertEqual(answer.rater_answer_judgment, 'False')
