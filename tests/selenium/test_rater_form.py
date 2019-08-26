from tests.selenium.base import SeleniumBaseRemoteTest


class RaterFormTest(SeleniumBaseRemoteTest):
    def test_blank(self):
        self.selenium.get(f'{self.live_server_url}/rater_form')
        self.assertTrue(True)
