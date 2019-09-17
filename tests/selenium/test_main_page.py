from selenium.common.exceptions import NoSuchElementException
from tests.utils import CatchInvalidSeleniumException
from workflow.models import Item, Rater, Workflow
from tests.selenium.base import SeleniumBaseRemoteTest

LOGOUT_XPATH = '//h3/a[contains(., "logout")]'
WORKFLOW_PAGE_XPATH = '//h3/a[contains(., "workflow page")]'
SIGN_IN_XPATH = '//h3/a[contains(., "sign in")]'
SIGN_UP_XPATH = '//h3/a[contains(., "sign up")]'


class MainPageTest(SeleniumBaseRemoteTest):

    def test_without_login(self):
        Item.objects.create(url='www.test.com', category='test_category', is_active=True)
        for x in range(1, 5):
            workflow = Workflow.objects.create(
                api_id=x,
                name=x,
                instruction=x,
                judgment=x,
                prediction=x)
        Rater.objects.create(
            email='test_main@test.com',
            api_id='test_main',
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

        selenium.get(f'{self.live_server_url}')
        sign_in_text = [sign_in.text for sign_in in selenium.find_elements_by_xpath(SIGN_IN_XPATH)]
        sign_up_text = [sign_up.text for sign_up in selenium.find_elements_by_xpath(SIGN_UP_XPATH)]

        self.assertEqual(len(sign_in_text), 1)
        self.assertEqual(len(sign_up_text), 1)

        with CatchInvalidSeleniumException(self):
            with self.assertRaises(NoSuchElementException):
                selenium.find_elements_by_id(LOGOUT_XPATH)
            with self.assertRaises(NoSuchElementException):
                selenium.find_elements_by_id(WORKFLOW_PAGE_XPATH)

    def test_with_login(self):
        Item.objects.create(id=1, url='www.test.com', category='test_category', is_active=True)
        for x in range(1, 5):
            workflow = Workflow.objects.create(
                api_id=x,
                name=x,
                instruction=x,
                judgment=x,
                prediction=x)
        rater = Rater.objects.create(
            email='test_main@test.com',
            api_id='test_main',
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
        selenium.get(f'{self.live_server_url}')

        logout_text = [logout.text for logout in selenium.find_elements_by_xpath(LOGOUT_XPATH)]
        workflow_page_text = [
            workflow_page.text for workflow_page in selenium.find_elements_by_xpath(WORKFLOW_PAGE_XPATH)
        ]

        self.assertEqual(len(logout_text), 1)
        self.assertEqual(len(workflow_page_text), 1)

        with CatchInvalidSeleniumException(self):
            with self.assertRaises(NoSuchElementException):
                selenium.find_elements_by_id(SIGN_IN_XPATH)
            with self.assertRaises(NoSuchElementException):
                selenium.find_elements_by_id(SIGN_UP_XPATH)
