import os
from datetime import datetime
from django.db import IntegrityError
from django.db.models import F, Count
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.clickjacking import xframe_options_exempt
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from boto3.exceptions import Boto3Error

from .email_templates import registration_rater_template
from .tasks import send_mail_task
from .form import SignInForm, SignUpForm, EvidenceInputWorkflowForm, JudgmentForm, WithoutEvidenceWorkflowForm, \
    MTurkRegisterForm
from .models import Rater, Answer, Item, Workflow, ItemWorkflow, Assignment
from .choices import WORKFLOW_TYPE_CHOICES
from . import alerts
from .services.mturk import MTurkConnection

NONE_OF_THE_ABOVE_TUPLE = (None, 'None of the above provides useful evidence')
VERSION = os.getenv('VERSION', 'dev.09.10.2019.1')


def main_view(request):
    rater_id = request.session.get('rater_id')
    if rater_id:
        try:
            rater = Rater.objects.get(api_id=rater_id)
            all_items = Item.objects.filter(is_active=True).count()
            used_items = len({answer.item_id for answer in Answer.objects.filter(
                rater=rater) if answer.item.is_active is True})
            return render(request, 'workflow/main.html', {
                'rater': rater_id,
                'all_items': all_items,
                'used_items': used_items,
                'version': VERSION})
        except ObjectDoesNotExist:
            return render(request, 'workflow/main.html', {'rater': None, 'version': VERSION})
    return render(request, 'workflow/main.html', {'rater': rater_id, 'version': VERSION})


def sign_up(request):
    if request.method == 'POST':
        if not Workflow.objects.all().count():
            form = SignUpForm()
            return render(request, 'workflow/sign_up.html',
                          {'error': True, 'form': form, 'messages':
                              ['There is no Workflow in database',
                               'Please, create at least one'], 'version': VERSION})
        try:
            api_id = '{}{}'.format(request.POST.get('email').split('@', 1)[0], datetime.today().date())
            form = SignUpForm(request.POST)
            if form.is_valid():
                rater = Rater(api_id=api_id, workflow=Workflow.objects.order_by('?').first())
                rater.age = request.POST.get('age')
                rater.email = request.POST.get('email')
                rater.gender = request.POST.get('gender')
                rater.location = request.POST.get('location')
                rater.save()
                request.session['rater_id'] = api_id
                rater_id = api_id

                subject, body = registration_rater_template
                send_mail_task.delay(to=[form.cleaned_data['email']],
                                     subject=subject,
                                     body=body.format(rater_id))
                all_items = Item.objects.all().count()
                return render(request, 'workflow/main.html', {
                    'new_rater': 'done',
                    'rater': rater_id,
                    'all_items': all_items,
                    'version': VERSION})
            errors = [value for value in form.errors.values()]
            form = SignUpForm()
            return render(request, 'workflow/sign_up.html',
                          {'error': True, 'form': form, 'messages':
                              [message for message in errors], 'version': VERSION})
        except IntegrityError:
            render(request, 'workflow/sign_up.html',
                   {'error': True, 'form': form, 'messages':
                       ['There is no Workflow in database',
                        'Please, create at least one'], 'version': VERSION})
    form = SignUpForm()
    return render(request, 'workflow/sign_up.html', {'form': form, 'version': VERSION})


def sign_in(request):
    if request.method == 'POST':
        form = SignInForm(request.POST)
        if form.is_valid():
            try:
                rater = Rater.objects.get(api_id=request.POST.get('api_id'))
                request.session['rater_id'] = rater.api_id
                all_items = Item.objects.all().count()
                used_items = len({answer.item_id for answer in Answer.objects.filter(rater=rater)})
                return render(request, 'workflow/main.html', {
                    'old_rater': 'done',
                    'rater': rater.api_id,
                    'all_items': all_items,
                    'used_items': used_items,
                    'version': VERSION})
            except ObjectDoesNotExist:
                return render(request, 'workflow/sign_in.html', {
                    'form': form,
                    'error': True,
                    'messages': alerts.INVALID_USER_SIGN_IN_ALERTS,
                    'version': VERSION})
        errors = [value for value in form.errors.values()]
        form = SignInForm()
        return render(request, 'workflow/sign_up.html',
                      {'error': True, 'form': form, 'messages':
                          [message for message in errors], 'version': VERSION})
    form = SignInForm()
    return render(request, 'workflow/sign_in.html', {'form': form, 'version': VERSION})


def logout(request):
    if not request.session.get('rater_id'):
        return render(request, 'workflow/sign_in.html', {
            'form': SignInForm(),
            'error': True,
            'messages': ['You are not signed in our system!'], 'version': VERSION})
    if request.method == 'POST':
        request.session.pop('rater_id')
        return render(request, 'workflow/main.html', {'logout': 'done', 'version': VERSION})

    return render(request, 'workflow/logout.html', {'version': VERSION})


def workflow_form(request, previous_url=None):  # noqa: too-many-locals
    rater_id = request.session.get('rater_id')
    if not rater_id:
        return render(request, 'workflow/sign_in.html', {
            'form': SignInForm(),
            'error': True,
            'messages': alerts.NOT_SIGNED_IN_USER_WORKFLOW_ALERTS,
            'version': VERSION})
    try:
        rater = Rater.objects.get(api_id=rater_id)
    except ObjectDoesNotExist:
        return render(request, 'workflow/main.html', {
            'error': True,
            'messages': alerts.INVALID_USER_ALERTS,
            'version': VERSION})
    try:
        workflow = rater.workflow
    except ObjectDoesNotExist:
        return render(request, 'workflow/main.html', {
            'error': True,
            'messages': alerts.INVALID_WORKFLOW_ALERTS,
            'rater': rater_id,
            'version': VERSION})

    def get_item(rater, previous_url):
        last_answer = None
        item = None
        if previous_url:
            last_answers = Answer.objects.filter(rater=rater).order_by('-answer_end')
            if last_answers.count() > 0:
                last_answer = last_answers[0]
                item = last_answer.item
        if not previous_url:
            used_items_for_user_ids = {answer.item_id for answer in Answer.objects.filter(rater=rater)}
            items_without_answers_for_user = Item.objects.filter(
                is_active=True).exclude(id__in=used_items_for_user_ids)
            if items_without_answers_for_user:
                item = items_without_answers_for_user[0]
        return {'item': item, 'last_answer': last_answer}

    def get_all_items_and_used_items(rater):
        all_items = Item.objects.filter(is_active=True).count()
        used_items = len({answer.item for answer in Answer.objects.filter(rater=rater, item__is_active=True)})

        return {'all_items': all_items, 'used_items': used_items}

    all_items = get_all_items_and_used_items(rater).get('all_items')
    used_items = get_all_items_and_used_items(rater).get('used_items')
    item = get_item(rater, previous_url).get('item')
    if not item and not previous_url:
        return render(request, 'workflow/main.html', {
            'error': True,
            'workflow': 'done',
            'rater': rater_id,
            'all_items': all_items,
            'used_items': used_items,
            'version': VERSION})

    if not item and previous_url:
        return render(request, 'workflow/main.html', {
            'error': True,
            'messages': alerts.INVALID_PREVIOUS_ITEM_ALERTS,
            'rater': rater_id,
            'all_items': all_items,
            'used_items': used_items,
            'version': VERSION})

    def get_no_workflow_form():
        return render(request, 'workflow/main.html', {
            'error': True,
            'messages': alerts.INVALID_WORKFLOW_ALERTS,
            'rater': rater_id,
            'version': VERSION})

    def get_form(rater, previous_url, workflow, messages=None, error=False):
        item_last_answer = get_item(rater, previous_url)
        item = item_last_answer.get('item')
        last_answer = item_last_answer.get('last_answer')
        all_items = get_all_items_and_used_items(rater).get('all_items')
        used_items = get_all_items_and_used_items(rater).get('used_items')
        if not item:
            return render(request, 'workflow/main.html', {
                'error': True,
                'workflow': 'done',
                'rater': rater_id,
                'all_items': all_items,
                'used_items': used_items,
                'version': VERSION})
        form = None
        initial = {
            'item': item.url,
            'instruction': workflow.instruction,
            'corroborating_question': workflow.corroborating_question,
            'judgment_enough_information': workflow.judgment_enough_information,
            'judgment_misleading_item': workflow.judgment_misleading_item,
            'judgment_remove_reduce_inform_head': workflow.judgment_remove_reduce_inform_head,
            'judgment_question_remove': workflow.judgment_remove,
            'judgment_question_reduce': workflow.judgment_reduce,
            'judgment_question_inform': workflow.judgment_inform,
            'judgment_additional': workflow.judgment_additional,
            'prediction_question': workflow.prediction,
        }
        if last_answer and previous_url:
            initial['evidence_url'] = last_answer.evidence_url
            initial['rater_answer_evidence'] = last_answer.rater_answer_evidence
            initial['rater_answer_judgment'] = last_answer.rater_answer_judgment
            initial['judgment_additional_information'] = last_answer.judgment_additional_information
            initial['rater_answer_predict_a'] = last_answer.rater_answer_predict_a
            initial['rater_answer_predict_b'] = last_answer.rater_answer_predict_b
            initial['rater_answer_predict_c'] = last_answer.rater_answer_predict_c
            initial['rater_answer_judgment_misleading_item'] = last_answer.rater_answer_judgment_misleading_item
            initial['rater_answer_judgment_remove'] = last_answer.rater_answer_judgment_remove
            initial['rater_answer_judgment_reduce'] = last_answer.rater_answer_judgment_reduce
            initial['rater_answer_judgment_inform'] = last_answer.rater_answer_judgment_inform

        if workflow.type == workflow.type == WORKFLOW_TYPE_CHOICES.WITHOUT_EVIDENCE_URL_WORKFLOW:
            form = WithoutEvidenceWorkflowForm
        if workflow.type == WORKFLOW_TYPE_CHOICES.EVIDENCE_URL_INPUT_WORKFLOW:
            form = EvidenceInputWorkflowForm
        if workflow.type == WORKFLOW_TYPE_CHOICES.EVIDENCE_URLS_JUDGMENT_WORKFLOW:
            form = JudgmentForm
            try:
                top_five_urls = sorted([answer.get('evidence_url') for answer in
                                        Answer.objects.filter(
                                            item=item).values('evidence_url').exclude(
                                            evidence_url__isnull=True).annotate(
                                            total=Count('evidence_url')).order_by(
                                            '-total')[:5]])
                evidence_url_choices = [(url, url) for url in top_five_urls]
                evidence_url_choices.append(NONE_OF_THE_ABOVE_TUPLE)
                evidence_url_choices = tuple(evidence_url_choices)
                initial['evidence_url_choices'] = evidence_url_choices

            except (ObjectDoesNotExist, TypeError):
                return render(request, 'workflow/main.html', {
                    'error': True,
                    'messages': alerts.NO_ANSWERS_FOR_CORROBORATING_CHOICES_ALERTS,
                    'rater': rater_id,
                    'all_items': all_items,
                    'used_items': used_items,
                    'version': VERSION})
        if not form:
            return get_no_workflow_form()

        try:
            form = form(initial=initial)
            return render(request, 'workflow/workflow_form.html', {
                'form': form,
                'item': item,
                'workflow': workflow,
                'rater_id': Rater.objects.get(api_id=rater_id).id,
                'messages': messages,
                'error': error,
                'previous_url': previous_url,
                'version': VERSION})
        except ObjectDoesNotExist:
            return render(request, 'workflow/main.html', {'workflow': 'done', 'rater': rater_id, 'version': VERSION})

    def post_form():  # noqa: too-many-locals
        previous_url = None
        if request.POST.get('previous_url') == 'True':
            previous_url = True
        form = None
        evidence_url = None
        if workflow.type == WORKFLOW_TYPE_CHOICES.WITHOUT_EVIDENCE_URL_WORKFLOW:
            form = WithoutEvidenceWorkflowForm(request.POST)
        if workflow.type == WORKFLOW_TYPE_CHOICES.EVIDENCE_URL_INPUT_WORKFLOW:
            if request.POST.get('evidence_url') and request.POST.get('rater_answer_evidence') == 'True':
                evidence_url = request.POST.get('evidence_url')
            if request.POST.get('evidence_url') and request.POST.get('rater_answer_evidence') == 'False':
                return get_form(
                    rater=rater,
                    previous_url=previous_url,
                    workflow=workflow,
                    error=True,
                    messages=alerts.INPUTED_EVIDENCE_URL_WITHOUT_ANSWER_EVIDENCE)
            form = EvidenceInputWorkflowForm(request.POST)
        if workflow.type == WORKFLOW_TYPE_CHOICES.EVIDENCE_URLS_JUDGMENT_WORKFLOW:
            if request.POST.get('evidence_url') and request.POST.get('evidence_url') != 'None':
                evidence_url = request.POST.get('evidence_url')
            try:
                item = Item.objects.get(id=request.POST.get('item'))
                top_five_urls = sorted([answer.get('evidence_url') for answer in
                                        Answer.objects.filter(
                                            item=item).values('evidence_url').exclude(
                                            evidence_url__isnull=True).annotate(
                                            total=Count('evidence_url')).order_by(
                                            '-total')[:5]])
                evidence_url_choices = [(url, url) for url in top_five_urls]
                evidence_url_choices.append(NONE_OF_THE_ABOVE_TUPLE)
                evidence_url_choices = tuple(evidence_url_choices)
                form = JudgmentForm(request.POST, initial={
                    'evidence_url_choices': evidence_url_choices})
            except (ObjectDoesNotExist, TypeError):
                return render(request, 'workflow/main.html', {
                    'error': True,
                    'messages': alerts.NO_ANSWERS_FOR_CORROBORATING_CHOICES_ALERTS,
                    'rater': rater_id,
                    'version': VERSION})

        if form.is_valid():
            item = Item.objects.get(id=request.POST.get('item'))
            answer_start = request.POST.get('answer_start')
            answer_end = datetime.now()
            rater_answer_evidence = request.POST.get('rater_answer_evidence')
            rater_answer_judgment = request.POST.get('rater_answer_judgment')
            judgment_additional_information = request.POST.get('judgment_additional_information')
            rater_answer_predict_a = request.POST.get('rater_answer_predict_a')
            rater_answer_predict_b = request.POST.get('rater_answer_predict_b')
            rater_answer_predict_c = request.POST.get('rater_answer_predict_c')
            rater_answer_judgment_misleading_item = request.POST.get('rater_answer_judgment_misleading_item')
            rater_answer_judgment_remove = request.POST.get('rater_answer_judgment_remove')
            rater_answer_judgment_reduce = request.POST.get('rater_answer_judgment_reduce')
            rater_answer_judgment_inform = request.POST.get('rater_answer_judgment_inform')
            if rater_answer_judgment == 'False':
                judgment_additional_information = None
                rater_answer_predict_a = None
                rater_answer_predict_b = None
                rater_answer_predict_c = None
                rater_answer_judgment_misleading_item = None
                rater_answer_judgment_remove = None
                rater_answer_judgment_reduce = None
                rater_answer_judgment_inform = None
            try:
                new_answer, created = Answer.objects.get_or_create(
                    rater=rater,
                    workflow=workflow,
                    item=item,
                    defaults={
                        'answer_start': answer_start,
                        'answer_end': answer_end,
                        'judgment_additional_information': judgment_additional_information,
                        'rater_answer_evidence': rater_answer_evidence,
                        'rater_answer_judgment': rater_answer_judgment,
                        'rater_answer_predict_a': rater_answer_predict_a,
                        'rater_answer_predict_b': rater_answer_predict_b,
                        'rater_answer_predict_c': rater_answer_predict_c,
                        'evidence_url': evidence_url,
                        'rater_answer_judgment_misleading_item': rater_answer_judgment_misleading_item,
                        'rater_answer_judgment_remove': rater_answer_judgment_remove,
                        'rater_answer_judgment_reduce': rater_answer_judgment_reduce,
                        'rater_answer_judgment_inform': rater_answer_judgment_inform,
                    })
                new_answer.answer_start = answer_start
                new_answer.answer_end = answer_end
                new_answer.rater_answer_evidence = rater_answer_evidence
                new_answer.rater_answer_judgment = rater_answer_judgment
                new_answer.judgment_additional_information = judgment_additional_information
                new_answer.rater_answer_predict_a = rater_answer_predict_a
                new_answer.rater_answer_predict_b = rater_answer_predict_b
                new_answer.rater_answer_predict_c = rater_answer_predict_c
                new_answer.evidence_url = evidence_url
                new_answer.rater_answer_judgment_misleading_item = rater_answer_judgment_misleading_item
                new_answer.rater_answer_judgment_remove = rater_answer_judgment_remove
                new_answer.rater_answer_judgment_reduce = rater_answer_judgment_reduce
                new_answer.rater_answer_judgment_inform = rater_answer_judgment_inform
                new_answer.save()
                instance, created = ItemWorkflow.objects.get_or_create(
                    item=item,
                    workflow=workflow,
                    defaults={'raters_desired': 0, 'raters_actual': 1}
                )
                if not created:
                    instance.raters_actual = F('raters_actual') + 1
                    instance.save()

                return get_form(
                    rater=rater,
                    previous_url=previous_url,
                    workflow=workflow)
            except (Answer.MultipleObjectsReturned, IntegrityError):
                return get_form(
                    rater=rater,
                    previous_url=previous_url,
                    workflow=workflow,
                    error=True,
                    messages=alerts.INTEGRITY_ERROR_ALERTS)
        else:
            return get_form(
                rater=rater,
                previous_url=previous_url,
                workflow=workflow,
                error=True,
                messages=alerts.NOT_ALL_REQUIRED_FIELDS_ALERTS)

    if request.method == 'POST':
        return post_form()

    return get_form(rater=rater, previous_url=previous_url, workflow=workflow)


def previous_item(request):
    return workflow_form(request, previous_url=True)


@method_decorator(xframe_options_exempt, name='dispatch')
class MTurkRegister(TemplateView):
    http_method_names = ['get', 'post']
    template_name = 'workflow/mturk_register.html'
    form = MTurkRegisterForm
    disable_header = True

    def post(self, request, **kwargs):
        connection = self._create_connection(**kwargs)
        if request.POST.get('first_question'):  # TODO set to real element after form with questions will be created
            return self._post_form(request, connection, **kwargs)

        return self._post_register(request, connection, **kwargs)

    def _post_register(self, request, connection, **kwargs):
        worker_id = request.POST.get('workerId')
        hit_id = request.POST.get('hitId')
        assignment_id = request.POST.get('assignmentId')
        rater, _ = Rater.objects.get_or_create(worker_id=worker_id)
        if rater.rejected_state or rater.completed_register_state:

            connection.accept_assignment(assignment_id, 'deny', False)
            context = self.get_context_data(**kwargs)
            return self.render_to_response(context, status=200)

        if not rater.workflow:
            rater.workflow = Workflow.objects.order_by('?').first()
        rater.save()

        Assignment.objects.get_or_create(
            assignment_id=assignment_id,
            hit_id=hit_id,
            rater=rater,
        )
        request.session['worker_id'] = worker_id
        return render(request, self.template_name, {
            'form': self.form,
            'disable_header': self.disable_header,
            'version': VERSION,
        })

    def _post_form(self, request, connection, **kwargs):
        try:
            rater = Rater.objects.get(worker_id=request.session.get('worker_id'))
        except Rater.DoesNotExist:
            context = self.get_context_data(**kwargs)
            return self.render_to_response(context, status=404)  # TODO check what we need to return

        assignment = Assignment.objects.get(rater=rater, is_active=True)

        # if not self.form(request.POST).is_valid():
        #     rater.rejected_state = True
        #     rater.save()
        #     return connection.accept_assignment(self, 'deny', True)  # TODO return here after form created
        rater.completed_register_state = True
        rater.rejected_state = False
        rater.save()
        assignment.is_active = False
        assignment.save()
        return connection.accept_assignment(rater.assignment_id, 'accept', True)

    def _create_connection(self, **kwargs):
        try:
            return MTurkConnection()
        except Boto3Error:
            context = self.get_context_data(**kwargs)
            return self.render_to_response(context, status=500)
