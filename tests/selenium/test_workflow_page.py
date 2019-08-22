from django.contrib.auth import get_user_model

from workflow.models import Rater, Workflow, Item, Answer
from tests.selenium.base import SeleniumBaseRemoteTest


class WorkflowRegisterTest(SeleniumBaseRemoteTest):

    def test_answer(self):
        Item.objects.create(api_id=1, url='www.test.com', category='test_category')
        workflow = None
        for x in range(1, 5):
            workflow = Workflow.objects.create(
                api_id=x,
                name=x,
                instruction=x,
                judgment=x,
                prediction=x)
        Rater.objects.create(
            api_id=1,
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)
        User = get_user_model()
        temp_user = User.objects.create(username='admin')
        temp_user.set_password('password')

        selenium = self.selenium
        selenium.get(f'{self.live_server_url}')

        self.client.login(username='admin', password='password')

        session = self.client.session
        session['rater_id'] = 1
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
        self.assertEqual(answer.evidence_url, 'https://test.com')
