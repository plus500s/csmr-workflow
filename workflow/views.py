from datetime import datetime
from django.db import IntegrityError
from django.db.models import F, Count
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from .form import SignInForm, SignUpForm, WorkflowForm, JudgmentForm
from .models import Rater, Answer, Item, Workflow, ItemWorkflow

NONE_OF_THE_ABOVE_TUPLE = ('None of the above', 'None of the above')


def main_view(request):
    return render(request, 'workflow/main.html')


def sign_up(request):
    if request.method == 'POST':
        api_id = '{}{}'.format(request.POST.get('email').split('@', 1)[0], datetime.today().date())
        rater = Rater(api_id=api_id, workflow=Workflow.objects.order_by('?').first())
        form = SignUpForm(request.POST, instance=rater)
        if form.is_valid():
            request.session['rater_id'] = api_id
            form.save()
            return render(request, 'workflow/main.html', {'new_rater': 'done'})
        errors = [value for value in form.errors.values()]
        form = SignUpForm()
        return render(request, 'workflow/sign_up.html',
                      {'error': True, 'form': form, 'messages':
                          [message for message in errors]})
    form = SignUpForm()
    return render(request, 'workflow/sign_up.html', {'form': form})


def sign_in(request):
    if request.method == 'POST':
        form = SignInForm(request.POST)
        if form.is_valid():
            try:
                rater = Rater.objects.get(api_id=request.POST.get('api_id'))
                request.session['rater_id'] = rater.api_id
            except ObjectDoesNotExist:
                return render(request, 'workflow/sign_in.html', {
                    'form': form,
                    'error': True,
                    'messages': ['User with current api_id does not exist',
                                 'Please, try again or sign up as a new user.']})
            return render(request, 'workflow/main.html', {'old_rater': 'done'})
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


def workflow_form(request):  # noqa: too-many-locals
    if not request.session.get('rater_id'):
        return render(request, 'workflow/sign_in.html', {
            'form': SignInForm(),
            'error': True,
            'messages': ['You are not signed in our system!',
                         'Please, sign in to have an access to workflow page!']})

    rater_id = request.session.get('rater_id')
    try:
        rater = Rater.objects.get(api_id=rater_id)
    except ObjectDoesNotExist:
        return render(request, 'workflow/main.html', {
            'error': True,
            'messages': ['Invalid User, please, try again']})
    try:
        workflow = rater.workflow
    except ObjectDoesNotExist:
        return render(request, 'workflow/main.html', {
            'error': True,
            'messages': ['Got no Workflow for this User']})

    def get_item(rater):
        used_items_for_user_ids = {answer.item_id for answer in Answer.objects.filter(rater=rater)}
        items_without_answers_for_user = Item.objects.exclude(id__in=used_items_for_user_ids)
        item = None
        if items_without_answers_for_user:
            item = items_without_answers_for_user[0]
        return item

    item = get_item(rater)
    if not item:
        return render(request, 'workflow/main.html', {'error': True, 'workflow': 'done'})

    def get_no_workflow_form():
        return render(request, 'workflow/main.html', {
            'error': True,
            'messages': ['Got no Workflow for this User']})

    def get_form(item, workflow, messages=None, error=False):
        if not item:
            return render(request, 'workflow/main.html', {'error': True, 'workflow': 'done'})
        form = None
        initial = {
            'item': item.url,
            'instruction': workflow.instruction,
            'corroborating_question': workflow.corroborating_question,
            'judgment_question': workflow.judgment,
            'prediction_question': workflow.prediction,
        }
        if workflow.name == 'workflow1':
            form = WorkflowForm
        if workflow.name == 'workflow2':
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
                    'messages': ['Got no answers to create corroborating choices']})
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
                'error': error
            })
        except ObjectDoesNotExist:
            return render(request, 'workflow/main.html', {'workflow': 'done'})

    def post_form():
        form = None
        evidence_url = None
        if workflow.name == 'workflow1':
            if request.POST.get('evidence_url') and request.POST.get(
                    'rater_answer_evidence'):
                evidence_url = request.POST.get('evidence_url')
            form = WorkflowForm(request.POST)
        if workflow.name == 'workflow2':
            if request.POST.get('evidence_url') and request.POST.get('evidence_url') not in NONE_OF_THE_ABOVE_TUPLE:
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
                    'messages': ['Got no answers to create corroborating choices']})

        if form.is_valid():
            item = Item.objects.get(id=request.POST.get('item'))
            answer_start = request.POST.get('answer_start')
            answer_end = datetime.now()
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
                        item=get_item(rater),
                        workflow=workflow,
                        error=True,
                        messages=[
                            'Please, enter valid percentage for Prediction question.',
                            'Sum of A, B and C answers should be 100.'
                            'Please, try again.'])
            except TypeError:
                return get_form(
                    item=get_item(rater),
                    workflow=workflow,
                    error=True,
                    messages=[
                        'Please, enter valid percentage for Prediction question.',
                        'Please, try again.'])
            try:
                Answer.objects.create(
                    rater=rater,
                    workflow=workflow,
                    item=item,
                    answer_start=answer_start,
                    answer_end=answer_end,
                    rater_answer_judgment=rater_answer_judgment,
                    rater_answer_predict_a=rater_answer_predict_a,
                    rater_answer_predict_b=rater_answer_predict_b,
                    rater_answer_predict_c=rater_answer_predict_c,
                    evidence_url=evidence_url,
                )
                instance, created = ItemWorkflow.objects.get_or_create(
                    item=item,
                    workflow=workflow,
                    defaults={'raters_desired': 0, 'raters_actual': 1}
                )
                if not created:
                    instance.raters_actual = F('raters_actual') + 1
                    instance.save()
                return get_form(
                    item=get_item(rater),
                    workflow=workflow)
            except IntegrityError:
                return get_form(
                    item=get_item(rater),
                    workflow=workflow,
                    error=True,
                    messages=[
                        'Something went wrong.',
                        'Please, try again.'])
        else:
            return get_form(item=get_item(rater),
                            workflow=workflow,
                            error=True,
                            messages=[
                                'Not all required fields have been entered.',
                                'Please, try again.'])

    if request.method == 'POST':
        return post_form()

    return get_form(item=get_item(rater), workflow=workflow)
