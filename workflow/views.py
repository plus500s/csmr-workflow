from datetime import datetime
from django.db import IntegrityError
from django.db.models import F, Count
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist

from .email_templates import registration_rater_template
from .tasks import send_mail_task
from .form import SignInForm, SignUpForm, EvidenceInputWorkflowForm, JudgmentForm, WithoutEvidenceWorkflowForm
from .models import Rater, Answer, Item, Workflow, ItemWorkflow
from .choices import WORKFLOW_TYPE_CHOICES
from . import alerts

NONE_OF_THE_ABOVE_TUPLE = (None, 'None of the above provides useful evidence')


def main_view(request):
    rater_id = request.session.get('rater_id')
    if rater_id:
        try:
            rater = Rater.objects.get(api_id=rater_id)
            all_items = Item.objects.all().count()
            used_items = len({answer.item_id for answer in Answer.objects.filter(rater=rater)})
            return render(request, 'workflow/main.html', {
                'rater': rater_id,
                'all_items': all_items,
                'used_items': used_items})
        except ObjectDoesNotExist:
            return render(request, 'workflow/main.html', {'rater': None})
    return render(request, 'workflow/main.html', {'rater': rater_id})


def sign_up(request):
    if request.method == 'POST':
        try:
            api_id = '{}{}'.format(request.POST.get('email').split('@', 1)[0], datetime.today().date())
            rater = Rater(api_id=api_id, workflow=Workflow.objects.order_by('?').first())
            form = SignUpForm(request.POST, instance=rater)
            if form.is_valid():
                request.session['rater_id'] = api_id
                rater_id = api_id
                form.save()

                subject, body = registration_rater_template
                send_mail_task.delay(to=[form.cleaned_data['email']],
                                     subject=subject,
                                     body=body.format(rater_id))
                all_items = Item.objects.all().count()
                return render(request, 'workflow/main.html', {
                    'new_rater': 'done',
                    'rater': rater_id,
                    'all_items': all_items})
            errors = [value for value in form.errors.values()]
            form = SignUpForm()
            return render(request, 'workflow/sign_up.html',
                          {'error': True, 'form': form, 'messages':
                              [message for message in errors]})
        except IntegrityError:
            render(request, 'workflow/sign_up.html',
                   {'error': True, 'form': form, 'messages':
                       ['There is no Workflow in database',
                        'Please, create at least one']})
    form = SignUpForm()
    return render(request, 'workflow/sign_up.html', {'form': form})


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
                    'used_items': used_items})
            except ObjectDoesNotExist:
                return render(request, 'workflow/sign_in.html', {
                    'form': form,
                    'error': True,
                    'messages': alerts.INVALID_USER_SIGN_IN_ALERTS})
        errors = [value for value in form.errors.values()]
        form = SignInForm()
        return render(request, 'workflow/sign_up.html',
                      {'error': True, 'form': form, 'messages':
                          [message for message in errors]})
    form = SignInForm()
    return render(request, 'workflow/sign_in.html', {'form': form})


def logout(request):
    if not request.session.get('rater_id'):
        return render(request, 'workflow/sign_in.html', {
            'form': SignInForm(),
            'error': True,
            'messages': ['You are not signed in our system!']})
    if request.method == 'POST':
        request.session.pop('rater_id')
        return render(request, 'workflow/main.html', {'logout': 'done'})

    return render(request, 'workflow/logout.html')


def workflow_form(request, previous_url=None):  # noqa: too-many-locals
    rater_id = request.session.get('rater_id')
    if not rater_id:
        return render(request, 'workflow/sign_in.html', {
            'form': SignInForm(),
            'error': True,
            'messages': alerts.NOT_SIGNED_IN_USER_WORKFLOW_ALERTS})
    try:
        rater = Rater.objects.get(api_id=rater_id)
    except ObjectDoesNotExist:
        return render(request, 'workflow/main.html', {
            'error': True,
            'messages': alerts.INVALID_USER_ALERTS})
    try:
        workflow = rater.workflow
    except ObjectDoesNotExist:
        return render(request, 'workflow/main.html', {
            'error': True,
            'messages': alerts.INVALID_WORKFLOW_ALERTS,
            'rater': rater_id})

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
            items_without_answers_for_user = Item.objects.exclude(id__in=used_items_for_user_ids)
            if items_without_answers_for_user:
                item = items_without_answers_for_user[0]
        return {'item': item, 'last_answer': last_answer}

    def get_all_items_and_used_items(rater):
        all_items = Item.objects.all().count()
        used_items = len({answer.item_id for answer in Answer.objects.filter(rater=rater)})
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
            'used_items': used_items})

    if not item and previous_url:
        return render(request, 'workflow/main.html', {
            'error': True,
            'messages': alerts.INVALID_PREVIOUS_ITEM_ALERTS,
            'rater': rater_id,
            'all_items': all_items,
            'used_items': used_items})

    def get_no_workflow_form():
        return render(request, 'workflow/main.html', {
            'error': True,
            'messages': alerts.INVALID_WORKFLOW_ALERTS,
            'rater': rater_id})

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
                'used_items': used_items})
        form = None
        initial = {
            'item': item.url,
            'instruction': workflow.instruction,
            'corroborating_question': workflow.corroborating_question,
            'judgment_question': workflow.judgment,
            'prediction_question': workflow.prediction,
        }
        if last_answer and previous_url:
            initial['evidence_url'] = last_answer.evidence_url
            initial['rater_answer_evidence'] = last_answer.rater_answer_evidence
            initial['rater_answer_judgment'] = last_answer.rater_answer_judgment
            initial['rater_answer_predict_a'] = last_answer.rater_answer_predict_a
            initial['rater_answer_predict_b'] = last_answer.rater_answer_predict_b
            initial['rater_answer_predict_c'] = last_answer.rater_answer_predict_c

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
                    'used_items': used_items})
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
            })
        except ObjectDoesNotExist:
            return render(request, 'workflow/main.html', {'workflow': 'done', 'rater': rater_id})

    def post_form():  # noqa: too-many-locals
        previous_url = None
        if request.POST.get('previous_url') == 'True':
            previous_url = True
        form = None
        evidence_url = None
        if workflow.type == workflow.type == WORKFLOW_TYPE_CHOICES.WITHOUT_EVIDENCE_URL_WORKFLOW:
            form = WithoutEvidenceWorkflowForm(request.POST)
        if workflow.type == WORKFLOW_TYPE_CHOICES.EVIDENCE_URL_INPUT_WORKFLOW:
            if request.POST.get('evidence_url') and request.POST.get('rater_answer_evidence') == 'True':
                evidence_url = request.POST.get('evidence_url')
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
                    'rater': rater_id})

        if form.is_valid():
            item = Item.objects.get(id=request.POST.get('item'))
            answer_start = request.POST.get('answer_start')
            answer_end = datetime.now()
            rater_answer_evidence = request.POST.get('rater_answer_evidence')
            rater_answer_judgment = request.POST.get('rater_answer_judgment')
            rater_answer_predict_a = request.POST.get('rater_answer_predict_a')
            rater_answer_predict_b = request.POST.get('rater_answer_predict_b')
            rater_answer_predict_c = request.POST.get('rater_answer_predict_c')
            # check, that prediction answers are 100 in sum.
            try:
                prediction_sum = sum([int(rater_answer_predict_a),
                                      int(rater_answer_predict_b),
                                      int(rater_answer_predict_c)])
                if prediction_sum != 100:
                    return get_form(
                        rater=rater,
                        previous_url=previous_url,
                        workflow=workflow,
                        error=True,
                        messages=alerts.PREDICTION_QUESTIONS_ALERTS)
            except TypeError:
                return get_form(
                    rater=rater,
                    previous_url=previous_url,
                    workflow=workflow,
                    error=True,
                    messages=alerts.PREDICTION_QUESTIONS_ALERTS)

            previous_url = None
            try:
                new_answer, created = Answer.objects.get_or_create(
                    rater=rater,
                    workflow=workflow,
                    item=item,
                    defaults={
                        'answer_start': answer_start,
                        'answer_end': answer_end,
                        'rater_answer_evidence': rater_answer_evidence,
                        'rater_answer_judgment': rater_answer_judgment,
                        'rater_answer_predict_a': rater_answer_predict_a,
                        'rater_answer_predict_b': rater_answer_predict_b,
                        'rater_answer_predict_c': rater_answer_predict_c,
                        'evidence_url': evidence_url,
                    })
                new_answer.answer_start = answer_start
                new_answer.answer_end = answer_end
                new_answer.rater_answer_evidence = rater_answer_evidence
                new_answer.rater_answer_judgment = rater_answer_judgment
                new_answer.rater_answer_predict_a = rater_answer_predict_a
                new_answer.rater_answer_predict_b = rater_answer_predict_b
                new_answer.rater_answer_predict_c = rater_answer_predict_c
                new_answer.evidence_url = evidence_url
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
