from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from workflow.models import Rater, Workflow, Item, Answer
from tests.selenium.base import SeleniumBaseRemoteTest


class JudgmentRegisterTest(SeleniumBaseRemoteTest):

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
            email='test3@test.com',
            api_id='3',
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)
        answer_start = datetime.now()
        answer_end = datetime.now()
        answer = Answer.objects.create(
            id=3,
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

        session = self.client.session
        session['rater_id'] = '3'
        session['judge_item'] = 3
        session.save()
        selenium.add_cookie({'name': 'sessionid', 'value': session._SessionBase__session_key,
                             'secure': False, 'path': '/'})
        selenium.get(f'{self.live_server_url}/judgment_form')

        rater_answer_judgment = selenium.find_element_by_id('id_id_rater_answer_judgment_0_1')
        rater_answer_evidence = selenium.find_element_by_id('id_id_evidence_url_0_1')

        rater_answer_predict_a = selenium.find_element_by_id('id_rater_answer_predict_a')
        rater_answer_predict_b = selenium.find_element_by_id('id_rater_answer_predict_b')
        rater_answer_predict_c = selenium.find_element_by_id('id_rater_answer_predict_c')

        submit = selenium.find_element_by_id('submit')

        rater_answer_evidence.click()
        rater_answer_judgment.click()

        rater_answer_predict_a.send_keys('10')
        rater_answer_predict_b.send_keys('30')
        rater_answer_predict_c.send_keys('60')

        submit.click()

        answer = Answer.objects.exclude(id=answer.id).get(rater=rater, item=item, workflow=workflow)
        self.assertEqual(Answer.objects.all().count(), 2)
        self.assertEqual(answer.rater_answer_predict_a, '10')
        self.assertEqual(answer.rater_answer_predict_b, '30')
        self.assertEqual(answer.rater_answer_predict_c, '60')
        self.assertEqual(answer.rater.api_id, '3')
        self.assertEqual(answer.item.id, 3)
        self.assertEqual(answer.rater_answer_judgment, 'False')
        self.assertEqual(answer.evidence_url, 'https//test.evidence.com')


class JudgmentNoneEvidenceChoiceTest(SeleniumBaseRemoteTest):
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
            email='test5@test.com',
            api_id='5',
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)
        answer_start = datetime.now()
        answer_end = datetime.now()
        answer = Answer.objects.create(
            id=5,
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

        session = self.client.session
        session['rater_id'] = '5'
        session['judge_item'] = 5
        session.save()
        selenium.add_cookie({'name': 'sessionid', 'value': session._SessionBase__session_key,
                             'secure': False, 'path': '/'})
        selenium.get(f'{self.live_server_url}/judgment_form')

        rater_answer_judgment = selenium.find_element_by_id('id_id_rater_answer_judgment_0_1')
        rater_answer_evidence = selenium.find_element_by_id('id_id_evidence_url_0_2')

        rater_answer_predict_a = selenium.find_element_by_id('id_rater_answer_predict_a')
        rater_answer_predict_b = selenium.find_element_by_id('id_rater_answer_predict_b')
        rater_answer_predict_c = selenium.find_element_by_id('id_rater_answer_predict_c')

        submit = selenium.find_element_by_id('submit')

        rater_answer_judgment.click()
        rater_answer_evidence.click()
        rater_answer_predict_a.send_keys('10')
        rater_answer_predict_b.send_keys('20')
        rater_answer_predict_c.send_keys('70')

        submit.click()
        answer = Answer.objects.exclude(id=answer.id).get(rater=rater, item=item, workflow=workflow)
        self.assertEqual(Answer.objects.all().count(), 2)
        self.assertEqual(answer.rater_answer_predict_a, '10')
        self.assertEqual(answer.rater_answer_predict_b, '20')
        self.assertEqual(answer.rater_answer_predict_c, '70')
        self.assertEqual(answer.rater.api_id, '5')
        self.assertEqual(answer.item.id, 5)
        self.assertEqual(answer.rater_answer_judgment, 'False')
        self.assertEqual(answer.evidence_url, None)


class JudgmentWithoutEvidenceTest(SeleniumBaseRemoteTest):
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
            email='test5@test.com',
            api_id=5,
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)
        answer_start = datetime.now()
        answer_end = datetime.now()
        answer = Answer.objects.create(
            id=5,
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

        session = self.client.session
        session['rater_id'] = 5
        session['judge_item'] = 5
        session.save()
        selenium.add_cookie({'name': 'sessionid', 'value': session._SessionBase__session_key,
                             'secure': False, 'path': '/'})
        selenium.get(f'{self.live_server_url}/judgment_form')

        rater_answer_judgment = selenium.find_element_by_id('id_id_rater_answer_judgment_0_1')

        rater_answer_predict_a = selenium.find_element_by_id('id_rater_answer_predict_a')
        rater_answer_predict_b = selenium.find_element_by_id('id_rater_answer_predict_b')
        rater_answer_predict_c = selenium.find_element_by_id('id_rater_answer_predict_c')

        submit = selenium.find_element_by_id('submit')

        rater_answer_judgment.click()
        rater_answer_predict_a.send_keys('10')
        rater_answer_predict_b.send_keys('20')
        rater_answer_predict_c.send_keys('60')

        submit.click()
        with self.assertRaises(ObjectDoesNotExist):
            Answer.objects.exclude(id=answer.id).get(rater=rater, item=item, workflow=workflow)
        self.assertEqual(Answer.objects.all().count(), 1)


class JudgmentWithoutJudgmentTest(SeleniumBaseRemoteTest):
    def test_answer(self):
        item = Item.objects.create(id=6, api_id=6, url='www.test.com', category='test_category')
        workflow = None
        for x in range(1, 5):
            workflow = Workflow.objects.create(
                api_id=x,
                name=x,
                instruction=x,
                judgment=x,
                prediction=x)
        rater = Rater.objects.create(
            email='test6@test.com',
            api_id=6,
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)
        answer_start = datetime.now()
        answer_end = datetime.now()
        answer = Answer.objects.create(
            id=6,
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

        session = self.client.session
        session['rater_id'] = 6
        session['judge_item'] = 6
        session.save()
        selenium.add_cookie({'name': 'sessionid', 'value': session._SessionBase__session_key,
                             'secure': False, 'path': '/'})
        selenium.get(f'{self.live_server_url}/judgment_form')

        rater_answer_evidence = selenium.find_element_by_id('id_id_evidence_url_0_1')
        rater_answer_judgment = selenium.find_element_by_id('id_id_rater_answer_judgment_0_1')

        rater_answer_predict_a = selenium.find_element_by_id('id_rater_answer_predict_a')
        rater_answer_predict_b = selenium.find_element_by_id('id_rater_answer_predict_b')
        rater_answer_predict_c = selenium.find_element_by_id('id_rater_answer_predict_c')

        submit = selenium.find_element_by_id('submit')

        rater_answer_evidence.click()
        rater_answer_predict_a.send_keys('10')
        rater_answer_predict_b.send_keys('20')
        rater_answer_predict_c.send_keys('60')

        submit.click()
        with self.assertRaises(ObjectDoesNotExist):
            Answer.objects.exclude(id=answer.id).get(rater=rater, item=item, workflow=workflow)
        self.assertEqual(Answer.objects.all().count(), 1)


class JudgmentWithoutPredictionTest(SeleniumBaseRemoteTest):
    def test_answer(self):
        item = Item.objects.create(id=7, api_id=7, url='www.test.com', category='test_category')
        workflow = None
        for x in range(1, 5):
            workflow = Workflow.objects.create(
                api_id=x,
                name=x,
                instruction=x,
                judgment=x,
                prediction=x)
        rater = Rater.objects.create(
            email='test7@test.com',
            api_id=7,
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)
        answer_start = datetime.now()
        answer_end = datetime.now()
        answer = Answer.objects.create(
            id=7,
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

        session = self.client.session
        session['rater_id'] = 7
        session['judge_item'] = 7
        session.save()
        selenium.add_cookie({'name': 'sessionid', 'value': session._SessionBase__session_key,
                             'secure': False, 'path': '/'})
        selenium.get(f'{self.live_server_url}/judgment_form')

        rater_answer_evidence = selenium.find_element_by_id('id_id_evidence_url_0_1')
        rater_answer_judgment = selenium.find_element_by_id('id_id_rater_answer_judgment_0_1')

        rater_answer_predict_a = selenium.find_element_by_id('id_rater_answer_predict_a')
        rater_answer_predict_b = selenium.find_element_by_id('id_rater_answer_predict_b')
        rater_answer_predict_c = selenium.find_element_by_id('id_rater_answer_predict_c')

        submit = selenium.find_element_by_id('submit')

        rater_answer_evidence.click()
        rater_answer_judgment.click()

        submit.click()
        with self.assertRaises(ObjectDoesNotExist):
            Answer.objects.exclude(id=answer.id).get(rater=rater, item=item, workflow=workflow)
        self.assertEqual(Answer.objects.all().count(), 1)


class JudgmentWithInvalidTypePredictionTest(SeleniumBaseRemoteTest):
    def test_answer(self):
        item = Item.objects.create(id=8, api_id=8, url='www.test.com', category='test_category')
        workflow = None
        for x in range(1, 5):
            workflow = Workflow.objects.create(
                api_id=x,
                name=x,
                instruction=x,
                judgment=x,
                prediction=x)
        rater = Rater.objects.create(
            email='test8@test.com',
            api_id=8,
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)
        answer_start = datetime.now()
        answer_end = datetime.now()
        answer = Answer.objects.create(
            id=8,
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

        session = self.client.session
        session['rater_id'] = 8
        session['judge_item'] = 8
        session.save()
        selenium.add_cookie({'name': 'sessionid', 'value': session._SessionBase__session_key,
                             'secure': False, 'path': '/'})
        selenium.get(f'{self.live_server_url}/judgment_form')

        rater_answer_evidence = selenium.find_element_by_id('id_id_evidence_url_0_1')
        rater_answer_judgment = selenium.find_element_by_id('id_id_rater_answer_judgment_0_1')

        rater_answer_predict_a = selenium.find_element_by_id('id_rater_answer_predict_a')
        rater_answer_predict_b = selenium.find_element_by_id('id_rater_answer_predict_b')
        rater_answer_predict_c = selenium.find_element_by_id('id_rater_answer_predict_c')

        submit = selenium.find_element_by_id('submit')

        rater_answer_evidence.click()
        rater_answer_judgment.click()
        rater_answer_predict_a.send_keys('invalid_type_a')
        rater_answer_predict_b.send_keys('invalid_type_b')
        rater_answer_predict_c.send_keys('invalid_type_c')

        submit.click()
        with self.assertRaises(ObjectDoesNotExist):
            Answer.objects.exclude(id=answer.id).get(rater=rater, item=item, workflow=workflow)
        self.assertEqual(Answer.objects.all().count(), 1)


class JudgmentWithInvalidSumPredictionTest(SeleniumBaseRemoteTest):
    def test_answer(self):
        item = Item.objects.create(id=9, api_id=9, url='www.test.com', category='test_category')
        workflow = None
        for x in range(1, 5):
            workflow = Workflow.objects.create(
                api_id=x,
                name=x,
                instruction=x,
                judgment=x,
                prediction=x)
        rater = Rater.objects.create(
            email='test9@test.com',
            api_id=9,
            age=10,
            gender='m',
            location='Kiev',
            workflow=workflow)
        answer_start = datetime.now()
        answer_end = datetime.now()
        answer = Answer.objects.create(
            id=9,
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

        session = self.client.session
        session['rater_id'] = 9
        session['judge_item'] = 9
        session.save()
        selenium.add_cookie({'name': 'sessionid', 'value': session._SessionBase__session_key,
                             'secure': False, 'path': '/'})
        selenium.get(f'{self.live_server_url}/judgment_form')

        rater_answer_evidence = selenium.find_element_by_id('id_id_evidence_url_0_1')
        rater_answer_judgment = selenium.find_element_by_id('id_id_rater_answer_judgment_0_1')

        rater_answer_predict_a = selenium.find_element_by_id('id_rater_answer_predict_a')
        rater_answer_predict_b = selenium.find_element_by_id('id_rater_answer_predict_b')
        rater_answer_predict_c = selenium.find_element_by_id('id_rater_answer_predict_c')

        submit = selenium.find_element_by_id('submit')

        rater_answer_evidence.click()
        rater_answer_judgment.click()
        rater_answer_predict_a.send_keys('100')
        rater_answer_predict_b.send_keys('100')
        rater_answer_predict_c.send_keys('100')

        submit.click()
        with self.assertRaises(ObjectDoesNotExist):
            Answer.objects.exclude(id=answer.id).get(rater=rater, item=item, workflow=workflow)
        self.assertEqual(Answer.objects.all().count(), 1)
