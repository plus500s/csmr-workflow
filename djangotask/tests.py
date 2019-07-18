import time

from django.test import LiveServerTestCase, override_settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from .models import Rater
from selenium.webdriver.remote.webdriver import WebDriver


@override_settings(ALLOWED_HOSTS=['*'])
class RaterRegisterTest(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        cls.host = "django"
        cls.port = 20000
        super(RaterRegisterTest, cls).setUpClass()

    def setUp(self):
        self.selenium = WebDriver('http://172.20.0.2:4444/wd/hub', {'browserName': 'firefox'})
        super(RaterRegisterTest, self).setUp()

    def tearDown(self):
        self.selenium.quit()
        super(RaterRegisterTest, self).tearDown()

    def test_register(self):
        selenium = self.selenium
        selenium.get(f'{self.live_server_url}/taskone/')
        print(selenium.page_source)

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

        print(selenium.page_source)

        self.assertEqual(Rater.objects.all().count(), 1)
