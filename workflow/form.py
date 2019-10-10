from django import forms
from django.forms import Form

from .fields import RangeSliderField, UrlItemField, ModelInitialTextAreaField, EvidenceUrlChoicesField

from .choices import EVIDENCE_CHOICES, JUDGMENT_CHOICES, JUDGMENT_REMOVE_CHOICES, JUDGMENT_REDUCE_CHOICES, \
    JUDGMENT_INFORM_CHOICES, JUDGMENT_MISLEADING_ITEM_CHOICES

TEXT_WIDTH = 'width:300px'


class SignUpForm(Form):
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
    judgment_enough_information = ModelInitialTextAreaField(
        label='<h3><strong>Judgment questions:</strong></h3>',
        disabled=True,
        required=False)
    rater_answer_judgment = forms.ChoiceField(
        label='',
        choices=JUDGMENT_CHOICES,
        widget=forms.RadioSelect)
    judgment_misleading_item = ModelInitialTextAreaField(
        label='',
        disabled=True,
        required=False)
    rater_answer_judgment_misleading_item = forms.ChoiceField(
        label='',
        choices=JUDGMENT_MISLEADING_ITEM_CHOICES,
        widget=forms.RadioSelect)
    judgment_remove_reduce_inform_head = ModelInitialTextAreaField(
        label='',
        disabled=True,
        required=False)
    judgment_question_remove = ModelInitialTextAreaField(
        label='',
        disabled=True,
        required=False)
    rater_answer_judgment_remove = forms.ChoiceField(
        label='',
        choices=JUDGMENT_REMOVE_CHOICES,
        widget=forms.RadioSelect)
    judgment_question_reduce = ModelInitialTextAreaField(
        label='',
        disabled=True,
        required=False)
    rater_answer_judgment_reduce = forms.ChoiceField(
        label='',
        choices=JUDGMENT_REDUCE_CHOICES,
        widget=forms.RadioSelect)
    judgment_question_inform = ModelInitialTextAreaField(
        label='',
        disabled=True,
        required=False)
    rater_answer_judgment_inform = forms.ChoiceField(
        label='',
        choices=JUDGMENT_INFORM_CHOICES,
        widget=forms.RadioSelect)
    judgment_additional = ModelInitialTextAreaField(
        disabled=True,
        required=False)
    judgment_additional_information = forms.CharField(
        label='',
        required=False,
        widget=forms.Textarea(attrs={'rows': 2}))
    prediction_question = ModelInitialTextAreaField(
        label='<h3><strong>Prediction question:</strong></h3>',
        disabled=True,
        required=False)
    rater_answer_predict_a = RangeSliderField(
        max=100,
        min=0,
        step=5,
        label='Remove. Out of 100 respondents, how many will say the item should be removed?',
        name='rater_answer_predict_a'
    )
    rater_answer_predict_b = RangeSliderField(
        max=100,
        min=0,
        step=5,
        label='Reduce. Out of 100 respondents, how many will say the item’s audience should be reduced?',
        name='rater_answer_predict_b'
    )
    rater_answer_predict_c = RangeSliderField(
        max=100,
        min=0,
        step=5,
        label='Inform. Out of 100 respondents, '
              'how many will say that users should be informed that the item is misleading?',
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
                   'judgment_enough_information', 'rater_answer_judgment',  'judgment_misleading_item',
                   'rater_answer_judgment_misleading_item', 'judgment_remove_reduce_inform_head',
                   'judgment_question_remove', 'rater_answer_judgment_remove', 'judgment_question_reduce',
                   'rater_answer_judgment_reduce', 'judgment_question_inform', 'rater_answer_judgment_inform',
                   'judgment_additional', 'judgment_additional_information', 'prediction_question',
                   'rater_answer_predict_a', 'rater_answer_predict_b', 'rater_answer_predict_c']


class JudgmentForm(BaseWorkflowForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            self.evidence_url_choices = kwargs.get('initial').get('evidence_url_choices')
        except AttributeError:
            self.evidence_url_choices = []
        self.fields['evidence_url'] = EvidenceUrlChoicesField(
            label='',
            choices=self.evidence_url_choices)
        self.fields['corroborating_question'] = ModelInitialTextAreaField(
            label='<h3><strong>Corroborating evidence:</strong></h3>',
            disabled=True,
            required=False)
        self.order_fields(['instruction', 'item', 'corroborating_question', 'evidence_url',
                           'judgment_enough_information', 'rater_answer_judgment',  'judgment_misleading_item',
                           'rater_answer_judgment_misleading_item', 'judgment_remove_reduce_inform_head',
                           'judgment_question_remove', 'rater_answer_judgment_remove', 'judgment_question_reduce',
                           'rater_answer_judgment_reduce', 'judgment_question_inform', 'rater_answer_judgment_inform',
                           'judgment_additional', 'judgment_additional_information', 'prediction_question',
                           'rater_answer_predict_a', 'rater_answer_predict_b', 'rater_answer_predict_c'])


class MTurkRegisterForm(Form):
    first_question = forms.Field(
        widget=forms.TextInput(attrs={'style': TEXT_WIDTH})
    )
    second_question = forms.Field(
        widget=forms.TextInput(attrs={'style': TEXT_WIDTH})
    )
    third_question = forms.Field(
        widget=forms.TextInput(attrs={'style': TEXT_WIDTH})
    )
