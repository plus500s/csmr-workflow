from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from workflow.models import Rater, Workflow, Item, Answer
from tests.selenium.base import SeleniumBaseRemoteTest


class JudgementRegisterTest(SeleniumBaseRemoteTest):

    def test_answer(self):
        item = Item.objects.create(id=3, api_id=3, url='www.test.com', category='test_category')
        workflow = None
        for x in range(1, 5):
            workflow = Workflow.objects.create(
                api_id=x,
                name=x,
                instruction=x,
                judgment=x,
                prediction=x)
        rater = Rater.objects.create(
            api_id=3,
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)
        answer_start = datetime.now()
        answer_end = datetime.now()
        answer = Answer.objects.create(
            pk=3,
            rater=rater,
            item=item,
            workflow=workflow,
            answer_start=answer_start,
            answer_end=answer_end,
            evidence_url='https//test.evidence.com'
        )
        User = get_user_model()
        temp_user = User.objects.create(username='admin')
        temp_user.set_password('password')

        selenium = self.selenium
        selenium.get(self.live_server_url)

        self.client.login(username='admin', password='password')

        session = self.client.session
        session['rater_id'] = 3
        session['judge_item'] = 3
        session.save()
        selenium.add_cookie({'name': 'sessionid', 'value': session._SessionBase__session_key,
                             'secure': False, 'path': '/'})
        selenium.get(f'{self.live_server_url}/judgement_form')

        rater_answer_judgement = selenium.find_element_by_id('id_id_rater_answer_judgment_0_1')
        rater_answer_evidence = selenium.find_element_by_id('id_id_evidence_url_0_1')

        rater_answer_predict_a = selenium.find_element_by_id('id_rater_answer_predict_a')
        rater_answer_predict_b = selenium.find_element_by_id('id_rater_answer_predict_b')
        rater_answer_predict_c = selenium.find_element_by_id('id_rater_answer_predict_c')

        submit = selenium.find_element_by_id('submit')

        rater_answer_evidence.click()
        rater_answer_judgement.click()

        rater_answer_predict_a.send_keys('10')
        rater_answer_predict_b.send_keys('15')
        rater_answer_predict_c.send_keys('20')

        submit.click()

        answer = Answer.objects.exclude(id=answer.id).get(rater=rater, item=item, workflow=workflow)
        self.assertEqual(Answer.objects.all().count(), 2)
        self.assertEqual(answer.rater_answer_predict_a, '10')
        self.assertEqual(answer.rater.api_id, 3)
        self.assertEqual(answer.item.id, 3)
        self.assertEqual(answer.rater_answer_judgment, 'False')
        self.assertEqual(answer.evidence_url, 'https//test.evidence.com')


class JudgementFailureTest(SeleniumBaseRemoteTest):
    def test_answer(self):
        item = Item.objects.create(id=4, api_id=4, url='www.test.com', category='test_category')
        workflow = None
        for x in range(1, 5):
            workflow = Workflow.objects.create(
                api_id=x,
                name=x,
                instruction=x,
                judgment=x,
                prediction=x)
        rater = Rater.objects.create(
            api_id=4,
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)
        answer_start = datetime.now()
        answer_end = datetime.now()
        answer = Answer.objects.create(
            pk=4,
            rater=rater,
            item=item,
            workflow=workflow,
            answer_start=answer_start,
            answer_end=answer_end,
            evidence_url='https//test.evidence.com'
        )
        User = get_user_model()
        temp_user = User.objects.create(username='admin')
        temp_user.set_password('password')

        selenium = self.selenium
        selenium.get(self.live_server_url)

        self.client.login(username='admin', password='password')

        session = self.client.session
        session['rater_id'] = 4
        session['judge_item'] = 4
        session.save()
        selenium.add_cookie({'name': 'sessionid', 'value': session._SessionBase__session_key,
                             'secure': False, 'path': '/'})
        selenium.get(f'{self.live_server_url}/judgement_form')

        rater_answer_judgement = selenium.find_element_by_id('id_id_rater_answer_judgment_0_1')

        rater_answer_predict_a = selenium.find_element_by_id('id_rater_answer_predict_a')
        rater_answer_predict_b = selenium.find_element_by_id('id_rater_answer_predict_b')
        rater_answer_predict_c = selenium.find_element_by_id('id_rater_answer_predict_c')

        submit = selenium.find_element_by_id('submit')

        rater_answer_judgement.click()
        rater_answer_predict_a.send_keys('10')
        rater_answer_predict_b.send_keys('15')
        rater_answer_predict_c.send_keys('20')

        submit.click()
        with self.assertRaises(ObjectDoesNotExist):
            Answer.objects.exclude(id=answer.id).get(rater=rater, item=item, workflow=workflow)
        self.assertEqual(Answer.objects.all().count(), 1)


class JudgementNoneEvidenceChoiceTest(SeleniumBaseRemoteTest):
    def test_answer(self):
        item = Item.objects.create(id=5, api_id=5, url='www.test.com', category='test_category')
        workflow = None
        for x in range(1, 5):
            workflow = Workflow.objects.create(
                api_id=x,
                name=x,
                instruction=x,
                judgment=x,
                prediction=x)
        rater = Rater.objects.create(
            api_id=5,
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)
        answer_start = datetime.now()
        answer_end = datetime.now()
        answer = Answer.objects.create(
            pk=5,
            rater=rater,
            item=item,
            workflow=workflow,
            answer_start=answer_start,
            answer_end=answer_end,
            evidence_url='https//test.evidence.com'
        )
        User = get_user_model()
        temp_user = User.objects.create(username='admin')
        temp_user.set_password('password')

        selenium = self.selenium
        selenium.get(self.live_server_url)

        self.client.login(username='admin', password='password')

        session = self.client.session
        session['rater_id'] = 5
        session['judge_item'] = 5
        session.save()
        selenium.add_cookie({'name': 'sessionid', 'value': session._SessionBase__session_key,
                             'secure': False, 'path': '/'})
        selenium.get(f'{self.live_server_url}/judgement_form')

        rater_answer_judgement = selenium.find_element_by_id('id_id_rater_answer_judgment_0_1')
        rater_answer_evidence = selenium.find_element_by_id('id_id_evidence_url_0_2')

        rater_answer_predict_a = selenium.find_element_by_id('id_rater_answer_predict_a')
        rater_answer_predict_b = selenium.find_element_by_id('id_rater_answer_predict_b')
        rater_answer_predict_c = selenium.find_element_by_id('id_rater_answer_predict_c')

        submit = selenium.find_element_by_id('submit')

        rater_answer_judgement.click()
        rater_answer_evidence.click()
        rater_answer_predict_a.send_keys('10')
        rater_answer_predict_b.send_keys('15')
        rater_answer_predict_c.send_keys('20')

        submit.click()
        answer = Answer.objects.exclude(id=answer.id).get(rater=rater, item=item, workflow=workflow)
        self.assertEqual(Answer.objects.all().count(), 2)
        self.assertEqual(answer.rater_answer_predict_a, '10')
        self.assertEqual(answer.rater.api_id, 5)
        self.assertEqual(answer.item.id, 5)
        self.assertEqual(answer.rater_answer_judgment, 'False')
        self.assertEqual(answer.evidence_url, None)
