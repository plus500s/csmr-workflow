from django import forms
from django.forms import ModelForm, Form

from .choices import EVIDENCE_CHOICES, JUDGEMENT_CHOICES
from .models import Rater


class RaterForm(ModelForm):
    class Meta:
        model = Rater
        fields = ['api_id', 'age', 'gender', 'location']


class WorkflowForm(Form):
    instruction = forms.Field(
        disabled=True,
        widget=forms.TextInput,
        required=False)
    item = forms.URLField(
        disabled=True,
        required=False)
    rater_answer_evidence = forms.ChoiceField(
        label='<strong>Corroborating evidence:</strong> '
              '<br>Were you able to find any corroborating evidence?',
        choices=EVIDENCE_CHOICES,
        widget=forms.RadioSelect)
    evidence_url = forms.URLField(
        label='If Yes, please provide the URL you used to make your judjement',
        required=False)
    judgement_question = forms.Field(
        label='<strong>Judgement question:</strong>',
        disabled=True,
        widget=forms.TextInput,
        required=False)
    rater_answer_judgment = forms.ChoiceField(
        label='',
        choices=JUDGEMENT_CHOICES,
        widget=forms.RadioSelect,
        required=False)
    prediction_question = forms.Field(
        label='<stromg>Prediction question:</strong>',
        disabled=True,
        widget=forms.TextInput,
        required=False)
    rater_answer_predict_a = forms.IntegerField(
        label='A',
        required=False,
        widget=forms.NumberInput(attrs={'style': 'width:100px'}))
    rater_answer_predict_b = forms.IntegerField(
        label='B',
        required=False,
        widget=forms.NumberInput(attrs={'style': 'width:100px'}))
    rater_answer_predict_c = forms.IntegerField(
        label='C',
        required=False,
        widget=forms.NumberInput(attrs={'style': 'width:100px'}))
