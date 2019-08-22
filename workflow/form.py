from django.forms import ModelForm
from .models import Rater


class RaterForm(ModelForm):
    class Meta:
        model = Rater
        fields = ['api_id', 'age', 'gender', 'location']
