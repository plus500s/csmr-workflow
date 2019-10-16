from datetime import datetime
from unittest import mock
from workflow.models import Rater, Workflow
from tests.selenium.base import SeleniumBaseRemoteTest


class SignUpTest(SeleniumBaseRemoteTest):

    def test_register_with_invalid_data(self):
        for x in range(1, 10):
            Workflow.objects.create(
                api_id=x,
                name=x,
                instruction=x,
                judgment_enough_information=x,
                judgment_misleading_item=x,
                judgment_remove_reduce_inform_head=x,
                judgment_remove=x,
                judgment_reduce=x,
                judgment_inform=x,
                prediction=x,)

        selenium = self.selenium
        selenium.get(f'{self.live_server_url}/sign_up')

        email = selenium.find_element_by_id('id_email')
        age = selenium.find_element_by_id('id_age')
        gender = selenium.find_element_by_id('id_gender')
        location = selenium.find_element_by_id('id_location')
        submit = selenium.find_element_by_id('submit')

        email.send_keys('test')
        age.send_keys('15')
        gender.send_keys('m')
        location.send_keys('China')
        submit.click()
        raters_count = Rater.objects.all().count()

        self.assertEqual(raters_count, 0)

    @mock.patch('workflow.tasks.send_mail_task.delay')
    def test_register(self, _):
        for x in range(1, 10):
            Workflow.objects.create(
                api_id=x,
                name=x,
                instruction=x,
                judgment_enough_information=x,
                judgment_misleading_item=x,
                judgment_remove_reduce_inform_head=x,
                judgment_remove=x,
                judgment_reduce=x,
                judgment_inform=x,
                prediction=x, )

        selenium = self.selenium
        selenium.get(f'{self.live_server_url}/sign_up')

        email = selenium.find_element_by_id('id_email')
        age = selenium.find_element_by_id('id_age')
        gender = selenium.find_element_by_id('id_gender')
        location = selenium.find_element_by_id('id_location')
        submit = selenium.find_element_by_id('submit')

        email.send_keys('test@test.com')
        age.send_keys('15')
        gender.send_keys('m')
        location.send_keys('China')

        submit.click()
        api_id = '{}{}'.format('test', datetime.today().date())
        rater = Rater.objects.get(email='test@test.com')
        self.assertEqual(rater.age, '15')
        self.assertEqual(rater.location, 'China')
        self.assertEqual(rater.gender, 'm')
        self.assertEqual(rater.api_id, api_id)


class SignInTest(SeleniumBaseRemoteTest):
    SUCCESS_ALERTS = ['Rater authorized']
    UN_SUCCESS_ALERTS = ['User with current api_id does not exist',
                         'Please, try again or sign up as a new user.']

    def test_sign_in_with_invalid_data(self):
        for x in range(1, 10):
            workflow = Workflow.objects.create(
                api_id=x,
                name=x,
                instruction=x,
                judgment_enough_information=x,
                judgment_misleading_item=x,
                judgment_remove_reduce_inform_head=x,
                judgment_remove=x,
                judgment_reduce=x,
                judgment_inform=x,
                prediction=x, )

        Rater.objects.create(
            email='testsignin@test.com',
            api_id='test_sign_in',
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)
        selenium = self.selenium
        selenium.get(f'{self.live_server_url}/sign_in')

        api_id = selenium.find_element_by_id('id_api_id')
        submit = selenium.find_element_by_id('submit')

        api_id.send_keys('invalid_data')

        submit.click()
        alerts = selenium.find_elements_by_xpath('//div[@class="alert alert-success"]')
        for alert in alerts:
            self.assertTrue(alert.text.replace('\n×', '') in self.UN_SUCCESS_ALERTS)

    def test_sign_in(self):
        for x in range(1, 10):
            workflow = Workflow.objects.create(
                api_id=x,
                name=x,
                instruction=x,
                judgment_enough_information=x,
                judgment_misleading_item=x,
                judgment_remove_reduce_inform_head=x,
                judgment_remove=x,
                judgment_reduce=x,
                judgment_inform=x,
                prediction=x, )

        rater = Rater.objects.create(
            email='testsignin@test.com',
            api_id='test_sign_in',
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)
        selenium = self.selenium
        selenium.get(f'{self.live_server_url}/sign_in')

        api_id = selenium.find_element_by_id('id_api_id')
        submit = selenium.find_element_by_id('submit')

        api_id.send_keys('test_sign_in')

        submit.click()
        alerts = selenium.find_elements_by_xpath('//div[@class="alert alert-success"]')

        for alert in alerts:
            self.assertTrue(alert.text.replace('\n×', '') in self.SUCCESS_ALERTS)


class LogoutTest(SeleniumBaseRemoteTest):
    SUCCESS_ALERTS = ['Successful logout']
    UN_SUCCESS_ALERTS = ['You are not signed in our system!']

    def test_logout_without_login(self):
        for x in range(1, 10):
            workflow = Workflow.objects.create(
                api_id=x,
                name=x,
                instruction=x,
                judgment_enough_information=x,
                judgment_misleading_item=x,
                judgment_remove_reduce_inform_head=x,
                judgment_remove=x,
                judgment_reduce=x,
                judgment_inform=x,
                prediction=x,)

        Rater.objects.create(
            email='testslogout@test.com',
            api_id='test_logout',
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)
        selenium = self.selenium
        selenium.get(self.live_server_url)
        session = self.client.session
        session.pop('rater_id', None)
        session.save()
        selenium.add_cookie({'name': 'sessionid', 'value': session._SessionBase__session_key,
                             'secure': False, 'path': '/'})

        selenium.get(f'{self.live_server_url}/logout')

        alerts = selenium.find_elements_by_xpath('//div[@class="alert alert-success"]')
        for alert in alerts:
            self.assertTrue(alert.text.replace('\n×', '') in self.UN_SUCCESS_ALERTS)

    def test_logout(self):
        for x in range(1, 10):
            workflow = Workflow.objects.create(
                api_id=x,
                name=x,
                instruction=x,
                judgment_enough_information=x,
                judgment_misleading_item=x,
                judgment_remove_reduce_inform_head=x,
                judgment_remove=x,
                judgment_reduce=x,
                judgment_inform=x,
                prediction=x, )

        rater = Rater.objects.create(
            email='testlogout@test.com',
            api_id='test_logout',
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)
        selenium = self.selenium
        selenium.get(self.live_server_url)
        session = self.client.session
        session['rater_id'] = rater.api_id
        session.save()

        selenium.add_cookie({'name': 'sessionid', 'value': session._SessionBase__session_key,
                             'secure': False, 'path': '/'})
        selenium.get(f'{self.live_server_url}/logout')

        alerts = selenium.find_elements_by_xpath('//div[@class="alert alert-success"]')

        for alert in alerts:
            self.assertTrue(alert.text.replace('\n×', '') in self.SUCCESS_ALERTS)

