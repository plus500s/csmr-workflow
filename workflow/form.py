from django import forms
from django.forms import ModelForm, Form

from .choices import EVIDENCE_CHOICES, JUDGMENT_CHOICES
from .models import Rater

TEXT_WIDTH = 'width:300px'


class SignUpForm(ModelForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'style': TEXT_WIDTH})
    )
    age = forms.Field(
        widget=forms.TextInput(attrs={'style': TEXT_WIDTH})
    )
    gender = forms.Field(
        widget=forms.TextInput(attrs={'style': TEXT_WIDTH})
    )
    location = forms.Field(
        widget=forms.TextInput(attrs={'style': TEXT_WIDTH})
    )

    class Meta:
        model = Rater
        fields = ['email', 'age', 'gender', 'location']


class SignInForm(Form):
    api_id = forms.CharField(
        label='Please, enter your api_id to sign in:',
        widget=forms.TextInput(attrs={'style': TEXT_WIDTH})
    )


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
        label='If Yes, please provide the URL you used to make your judgment',
        required=False)
    judgment_question = forms.Field(
        label='<strong>Judgment question:</strong>',
        disabled=True,
        widget=forms.TextInput,
        required=False)
    rater_answer_judgment = forms.ChoiceField(
        label='',
        choices=JUDGMENT_CHOICES,
        widget=forms.RadioSelect)
    prediction_question = forms.Field(
        label='<stromg>Prediction question:</strong>',
        disabled=True,
        widget=forms.TextInput,
        required=False)
    rater_answer_predict_a = forms.IntegerField(
        max_value=100,
        min_value=0,
        label='A',
        widget=forms.NumberInput(attrs={'style': 'width:100px'}))
    rater_answer_predict_b = forms.IntegerField(
        max_value=100,
        min_value=0,
        label='B',
        widget=forms.NumberInput(attrs={'style': 'width:100px'}))
    rater_answer_predict_c = forms.IntegerField(
        max_value=100,
        min_value=0,
        label='C',
        widget=forms.NumberInput(attrs={'style': 'width:100px'}))


class JudgmentForm(WorkflowForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.evidence_url_choices = kwargs.get('initial').get('evidence_url_choices')
        except AttributeError:
            self.evidence_url_choices = []
        self.fields['evidence_url'] = forms.ChoiceField(
            label='Following are a list of links that are likely to contain corroborating '
                  'evidence. Select the link that you found most useful to make your judgment.',
            choices=self.evidence_url_choices,
            widget=forms.RadioSelect)
        self.fields.pop('rater_answer_evidence')
