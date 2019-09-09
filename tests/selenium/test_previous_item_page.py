from datetime import datetime

from workflow.models import Rater, Workflow, Item, Answer
from workflow.choices import WORKFLOW_TYPE_CHOICES
from tests.selenium.base import SeleniumBaseRemoteTest
from .utils import send_predict_keys, set_predict_keys_to_zero


WORKFLOW_NAME = 'workflow1'
WORKFLOW_TYPE = WORKFLOW_TYPE_CHOICES.WITHOUT_EVIDENCE_URL_WORKFLOW

WORKFLOW_DONE_ALERT_XPATH = '//div[@class="alert alert-success"]'
WARNING_ALERTS_XPATH = '//div[@class="alert alert-warning"]'

SIGN_IN_TEXT = ['Sign in']
SIGN_IN_XPATH = '//h1[@class="mt-2"]'


class PreviousItemTest(SeleniumBaseRemoteTest):
    def test_answer(self):
        previous_item = Item.objects.create(id=1, api_id=1, url='www.test.com', category='test_category1')
        next_item = Item.objects.create(id=2, api_id=2, url='www.testtest.com', category='test_category2')

        for x in range(1, 5):
            workflow = Workflow.objects.create(
                api_id=x,
                name=WORKFLOW_NAME,
                instruction=x,
                judgment=x,
                prediction=x,
                type=WORKFLOW_TYPE)
        rater = Rater.objects.create(
            email='test1@test.com',
            api_id='1',
            age='10',
            gender='m',
            location='Kiev',
            workflow=workflow)
        answer_start = datetime.now()
        answer_end = datetime.now()
        Answer.objects.create(
            id=1,
            rater=rater,
            item=previous_item,
            workflow=workflow,
            answer_start=answer_start,
            answer_end=answer_end,
            rater_answer_evidence='True',
            rater_answer_judgment='True',
            rater_answer_predict_a='10',
            rater_answer_predict_b='20',
            rater_answer_predict_c='70',
        )
        selenium = self.selenium
        selenium.get(self.live_server_url)
        session = self.client.session
        session['rater_id'] = '1'
        session.save()
        selenium.add_cookie({'name': 'sessionid', 'value': session._SessionBase__session_key,
                             'secure': False, 'path': '/'})
        selenium.get(f'{self.live_server_url}/previous_item')

        rater_answer_judgment_true = selenium.find_element_by_id('id_id_rater_answer_judgment_0_1')
        rater_answer_judgment_false = selenium.find_element_by_id('id_id_rater_answer_judgment_0_2')
        rater_answer_predict_a = selenium.find_element_by_id('id_rater_answer_predict_a')
        rater_answer_predict_b = selenium.find_element_by_id('id_rater_answer_predict_b')
        rater_answer_predict_c = selenium.find_element_by_id('id_rater_answer_predict_c')
        submit = selenium.find_element_by_id('submit')

        self.assertEqual(rater_answer_judgment_true.is_selected(), True)
        self.assertEqual(rater_answer_judgment_false.is_selected(), False)
        self.assertEqual(rater_answer_predict_a.get_attribute('value'), '10')
        self.assertEqual(rater_answer_predict_b.get_attribute('value'), '20')
        self.assertEqual(rater_answer_predict_c.get_attribute('value'), '70')

        set_predict_keys_to_zero(
            predict_a=rater_answer_predict_a,
            predict_b=rater_answer_predict_b,
            predict_c=rater_answer_predict_c,
            key_a=10,
            key_b=20,
            key_c=70)
        rater_answer_judgment_true.click()
        send_predict_keys(
            predict_a=rater_answer_predict_a,
            predict_b=rater_answer_predict_b,
            predict_c=rater_answer_predict_c,
            key_a=70,
            key_b=20,
            key_c=10)

        submit.click()
        self.assertEqual(Answer.objects.all().count(), 1)
        answer = Answer.objects.get(rater=rater, item=previous_item, workflow=workflow)
        self.assertEqual(answer.rater_answer_predict_a, '70')
        self.assertEqual(answer.rater_answer_predict_b, '20')
        self.assertEqual(answer.rater_answer_predict_c, '10')
        self.assertEqual(answer.rater.api_id, '1')
        self.assertEqual(answer.item.id, 1)
        self.assertEqual(answer.rater_answer_judgment, 'True')
