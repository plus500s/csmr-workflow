import os
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver import Firefox
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class SeleniumBaseRemoteTest(StaticLiveServerTestCase):
    host = os.getenv('TEST_HOST', 'tests')

    suppress_invalid_exception = True if host == 'localhost' else False

    def setUp(self):
        firefox_capabilities = DesiredCapabilities.FIREFOX
        if self.host == 'localhost':
            firefox_capabilities['marionette'] = False
            self.selenium = Firefox(capabilities=firefox_capabilities)
        else:
            self.selenium = WebDriver(command_executor='http://selenium-hub:4444/wd/hub',
                                      desired_capabilities=firefox_capabilities)
        super().setUp()

    def tearDown(self):
        self.selenium.quit()
        super().tearDown()
