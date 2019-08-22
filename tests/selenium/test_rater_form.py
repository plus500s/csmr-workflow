from workflow.models import Rater, Workflow, Answer
from tests.selenium.base import SeleniumBaseRemoteTest


class RaterRegisterTest(SeleniumBaseRemoteTest):

    def test_register_with_invalid_data(self):
        for x in range(1, 5):
            Workflow.objects.create(
                api_id=x,
                name=x,
                instruction=x,
                judgment=x,
                prediction=x)

        selenium = self.selenium
        selenium.get(f'{self.live_server_url}/rater_form')

        api_id = selenium.find_element_by_id('id_api_id')
        age = selenium.find_element_by_id('id_age')
        gender = selenium.find_element_by_id('id_gender')
        location = selenium.find_element_by_id('id_location')
        submit = selenium.find_element_by_id('submit')

        api_id.send_keys('jfgdg')
        age.send_keys('15')
        gender.send_keys('m')
        location.send_keys('China')
        submit.click()
        answers_count = Answer.objects.all().count()

        self.assertEqual(answers_count, 0)

    def test_register(self):
        for x in range(1,5):
            Workflow.objects.create(
                api_id=x,
                name=x,
                instruction=x,
                judgment=x,
                prediction=x)

        selenium = self.selenium
        selenium.get(f'{self.live_server_url}/rater_form')

        api_id = selenium.find_element_by_id('id_api_id')
        age = selenium.find_element_by_id('id_age')
        gender = selenium.find_element_by_id('id_gender')
        location = selenium.find_element_by_id('id_location')
        submit = selenium.find_element_by_id('submit')

        api_id.send_keys('1')
        age.send_keys('15')
        gender.send_keys('m')
        location.send_keys('China')

        submit.click()

        self.assertEqual(Rater.objects.all().count(), 1)
