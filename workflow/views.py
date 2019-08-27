from datetime import datetime
from django.db import IntegrityError
from django.db.models import F, Count
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from .form import RaterForm, WorkflowForm, JudgementForm
from .models import Rater, Answer, Item, Workflow, ItemWorkflow

NONE_OF_THE_ABOVE_TUPLE = ('None of the above', 'None of the above')


def main_view(request):
    return render(request, 'workflow/main.html')


def rater_form(request):
    if request.method == 'POST':
        rater = Rater(workflow=Workflow.objects.order_by('?').first())
        form = RaterForm(request.POST, instance=rater)
        if form.is_valid():
            request.session['rater_id'] = form.cleaned_data['api_id']
            request.session['item'] = 1
            request.session['judge_item'] = 1
            form.save()
            return render(request, 'workflow/main.html', {'rater': 'done'})
        errors = [value for value in form.errors.values()]
        form = RaterForm()
        return render(request, 'workflow/rater_form.html',
                      {'error': True, 'form': form, 'messages':
                          [message for message in errors]})
    form = RaterForm()
    return render(request, 'workflow/rater_form.html', {'form': form})


def workflow_form(request):
    def get_form(messages=None, error=False):
        rater_id = request.session.get('rater_id', False)
        if not rater_id:
            return render(request, 'workflow/workflow_form.html', {'error': True})
        try:
            workflow = Rater.objects.get(api_id=rater_id).workflow
            item = Item.objects.get(id=request.session['item'])
            form = WorkflowForm(initial={
                'item': item.url,
                'instruction': workflow.instruction,
                'judgement_question': workflow.judgment,
                'prediction_question': workflow.prediction,
            })
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

    if request.method == 'POST':
        form = WorkflowForm(request.POST)
        if form.is_valid():
            rater_id = get_object_or_404(Rater, api_id=request.session.get('rater_id'))
            item = Item.objects.get(id=request.POST.get('item'))
            answer_start = request.POST.get('answer_start')
            workflow = Workflow.objects.get(id=request.POST.get('workflow'))
            answer_end = datetime.now()
            rater_answer_judgment = request.POST.get('rater_answer_judgment')
            rater_answer_predict_a = request.POST.get('rater_answer_predict_a')
            rater_answer_predict_b = request.POST.get('rater_answer_predict_b')
            rater_answer_predict_c = request.POST.get('rater_answer_predict_c')
            evidence_url = None
            if request.POST.get('evidence_url') and request.POST.get(
                    'rater_answer_evidence'):
                evidence_url = request.POST.get('evidence_url')
            try:
                instance = Answer.objects.create(
                    rater=rater_id,
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
                if instance:
                    request.session['item'] += 1

                instance, created = ItemWorkflow.objects.get_or_create(
                    item=item,
                    workflow=workflow,
                    defaults={'raters_desired': 0, 'raters_actual': 1}
                )
                if not created:
                    instance.raters_actual = F('raters_actual') + 1
                    instance.save()
            except IntegrityError:
                return render(request, 'workflow/workflow_form.html',
                              {'error': True, 'form': form})

        else:
            return get_form(error=True,
                            messages=[
                                'Not all required fields have been entered.',
                                'Please, try again.'])
    return get_form()


def judgement_form(request):  # noqa: too-many-locals
    try:
        item = Item.objects.get(id=request.session['judge_item'])
        top_five_urls = sorted([answer.get('evidence_url') for answer in
                                Answer.objects.filter(
                                    item=item).values('evidence_url').annotate(
                                    total=Count('evidence_url')).order_by(
                                    '-total')[:5]])
        evidence_url_choices = [(url, url) for url in top_five_urls]
        evidence_url_choices.append(NONE_OF_THE_ABOVE_TUPLE)
        evidence_url_choices = tuple(evidence_url_choices)
    except (ObjectDoesNotExist, TypeError):
        return render(request, 'workflow/main.html', {'workflow': 'done'})

    def get_form(messages=None, error=False):
        rater_id = request.session.get('rater_id', False)
        if not rater_id:
            return render(request, 'workflow/judgement_form.html',
                          {'error': True})
        workflow = Rater.objects.get(api_id=rater_id).workflow
        try:
            item = Item.objects.get(id=request.session['judge_item'])
            form = JudgementForm(
                initial={
                    'evidence_url_choices': evidence_url_choices,
                    'item': item.url,
                    'instruction': workflow.instruction,
                    'judgement_question': workflow.judgment,
                    'prediction_question': workflow.prediction,
                })
            return render(request, 'workflow/judgement_form.html', {
                'form': form,
                'item': item,
                'workflow': workflow,
                'rater_id': Rater.objects.get(api_id=rater_id).id,
                'messages': messages,
                'error': error
            })
        except ObjectDoesNotExist:
            return render(request, 'workflow/main.html', {'workflow': 'done'})

    if request.method == 'POST':
        form = JudgementForm(request.POST, initial={
            'evidence_url_choices': evidence_url_choices})
        if form.is_valid():
            rater_id = get_object_or_404(Rater,
                                         api_id=request.session.get(
                                             'rater_id'))
            item = Item.objects.get(id=request.POST.get('item'))
            answer_start = request.POST.get('answer_start')
            workflow = Workflow.objects.get(id=request.POST.get('workflow'))
            answer_end = datetime.now()
            rater_answer_judgment = request.POST.get('rater_answer_judgment')
            rater_answer_predict_a = request.POST.get('rater_answer_predict_a')
            rater_answer_predict_b = request.POST.get('rater_answer_predict_b')
            rater_answer_predict_c = request.POST.get('rater_answer_predict_c')
            evidence_url = None
            if request.POST.get('evidence_url') and \
                    request.POST.get(
                        'evidence_url') not in NONE_OF_THE_ABOVE_TUPLE:
                evidence_url = request.POST.get('evidence_url')
            try:
                instance = Answer.objects.create(
                    rater=rater_id,
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
                if instance:
                    request.session['judge_item'] += 1
                instance, created = ItemWorkflow.objects.get_or_create(
                    item=item,
                    workflow=workflow,
                    defaults={'raters_desired': 0, 'raters_actual': 1}
                )
                if not created:
                    instance.raters_actual = F('raters_actual') + 1
                    instance.save()
            except IntegrityError:
                return render(request, 'workflow/judgement_form.html',
                              {'error': True})
        else:
            return get_form(error=True,
                            messages=[
                                'Not all required fields have been entered.',
                                'Please, try again.'])
    return get_form()
