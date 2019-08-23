from datetime import datetime
from django.db.models import F
from django.db.utils import IntegrityError
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from .form import RaterForm
from .models import Rater, Answer, Item, Workflow, ItemWorkflow


def main_view(request):
    return render(request, 'workflow/main.html')


def rater_form(request):
    if request.method == 'POST':
        rater = Rater(workflow=Workflow.objects.order_by('?').first())
        form = RaterForm(request.POST, instance=rater)
        if form.is_valid():
            request.session['rater_id'] = form.cleaned_data['api_id']
            request.session['item'] = 1
            form.save()
            return render(request, 'workflow/main.html', {'rater': 'done'})
        return render(request, 'workflow/rater_form.html', {'error': True})

    form = RaterForm()
    return render(request, 'workflow/rater_form.html', {'form': form})


def workflow_form(request):
    if request.method == 'POST':
        rater_id = get_object_or_404(Rater, api_id=request.session.get('rater_id'))
        item = Item.objects.get(id=request.POST.get('item'))
        answer_start = request.POST.get('answer_start')
        workflow = Workflow.objects.get(id=request.POST.get('workflow'))
        answer_end = datetime.now()
        rater_answer_judgment = request.POST.get('rater_answer_judgment')
        rater_answer_predict_a = request.POST.get('rater_answer_predict_a')
        rater_answer_predict_b = request.POST.get('rater_answer_predict_b')
        rater_answer_predict_c = request.POST.get('rater_answer_predict_c')

        try:

            instance = Answer.objects.create(
                rater=rater_id,
                workflow=workflow,
                item=item,
                answer_start=answer_start,
                answer_end=answer_end, rater_answer_judgment=rater_answer_judgment,
                rater_answer_predict_a=rater_answer_predict_a,
                rater_answer_predict_b=rater_answer_predict_b,
                rater_answer_predict_c=rater_answer_predict_c)

            if instance:
                request.session['item'] += 1

            instance, created = ItemWorkflow.objects.get_or_create(
                item=item,
                workflow=workflow,
                defaults={'raters_desired': 0, 'raters_actual': 1})

            if not created:
                instance.raters_actual = F('raters_actual') + 1
                instance.save()

        except IntegrityError:
            return render(request, 'workflow/workflow_form.html', {'error': True})

    rater_id = request.session.get('rater_id', False)
    if not rater_id:
        return render(request, 'workflow/workflow_form.html', {'error': True})

    form = RaterForm()

    workflow = Rater.objects.get(api_id=rater_id).workflow

    try:
        return render(request, 'workflow/workflow_form.html', {
            'form': form,
            'item': Item.objects.get(id=request.session['item']),
            'workflow': workflow,
            'rater_id': Rater.objects.get(api_id=rater_id).id,
        })
    except ObjectDoesNotExist:
        return render(request, 'workflow/main.html', {'workflow': 'done'})
