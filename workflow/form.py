from django import forms
from django.forms import ModelForm, Form

from .fields import RangeSliderField, UrlItemField, ModelInitialTextAreaField

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


class BaseWorkflowForm(Form):
    instruction = ModelInitialTextAreaField(
        label='<h3><strong>Instruction:</strong></h3>',
        disabled=True,
        required=False)
    item = UrlItemField(
        label='<h3><strong>Item:</strong></h3>',
        disabled=True,
        required=False)
    judgment_question = ModelInitialTextAreaField(
        label='<h3><strong>Judgment question:</strong></h3>',
        disabled=True,
        required=False)
    rater_answer_judgment = forms.ChoiceField(
        label='',
        choices=JUDGMENT_CHOICES,
        widget=forms.RadioSelect)
    prediction_question = ModelInitialTextAreaField(
        label='<h3><strong>Prediction question:</strong></h3>',
        disabled=True,
        required=False)
    rater_answer_predict_a = RangeSliderField(
        max=100,
        min=0,
        step=5,
        label='Yes',
        name='rater_answer_predict_a'
    )
    rater_answer_predict_b = RangeSliderField(
        max=100,
        min=0,
        step=5,
        label='No',
        name='rater_answer_predict_b'
    )
    rater_answer_predict_c = RangeSliderField(
        max=100,
        min=0,
        step=5,
        label='Not sure',
        name='rater_answer_predict_c'
    )


class WithoutEvidenceWorkflowForm(BaseWorkflowForm):
    pass


class EvidenceInputWorkflowForm(BaseWorkflowForm):
    corroborating_question = ModelInitialTextAreaField(
        label='<h3><strong>Corroborating evidence:</strong></h3>',
        disabled=True,
        required=False)
    rater_answer_evidence = forms.ChoiceField(
        label='',
        choices=EVIDENCE_CHOICES,
        widget=forms.RadioSelect)
    evidence_url = forms.URLField(
        label='If Yes, please provide the URL that provided the evidence you found most relevant and convincing.',
        required=False)

    field_order = ['instruction', 'item', 'corroborating_question', 'rater_answer_evidence', 'evidence_url',
                   'judgment_question', 'rater_answer_judgment', 'prediction_question', 'rater_answer_predict_a',
                   'rater_answer_predict_b', 'rater_answer_predict_c']


class JudgmentForm(BaseWorkflowForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            self.evidence_url_choices = kwargs.get('initial').get('evidence_url_choices')
        except AttributeError:
            self.evidence_url_choices = []
        self.fields['evidence_url'] = forms.ChoiceField(
            label='',
            choices=self.evidence_url_choices,
            widget=forms.RadioSelect)
        self.fields['corroborating_question'] = ModelInitialTextAreaField(
            label='<h3><strong>Corroborating evidence:</strong></h3>',
            disabled=True,
            required=False)
        self.order_fields(['instruction', 'item', 'corroborating_question', 'evidence_url',
                           'judgment_question', 'rater_answer_judgment', 'prediction_question',
                           'rater_answer_predict_a',
                           'rater_answer_predict_b', 'rater_answer_predict_c'])
