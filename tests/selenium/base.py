from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class SeleniumBaseRemoteTest(StaticLiveServerTestCase):
    host = 'tests'

    def setUp(self):
        firefox_capabilities = DesiredCapabilities.FIREFOX
        self.selenium = WebDriver(command_executor='http://selenium-hub:4444/wd/hub',
                                  desired_capabilities=firefox_capabilities)
        super().setUp()

    def tearDown(self):
        self.selenium.quit()
        super().tearDown()
