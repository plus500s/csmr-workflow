from django import forms
from .widgets import RangeSlider


class RangeSliderField(forms.CharField):
    def __init__(self, *args, **kwargs):
        self.name = kwargs.pop('name', '')
        self.min = kwargs.pop('min', 0)
        self.max = kwargs.pop('max', 100)
        self.step = kwargs.pop('step', 1)
        kwargs['widget'] = RangeSlider(self.min, self.max, self.step, self.name)
        if 'label' not in kwargs.keys():
            kwargs['label'] = False
        super().__init__(*args, **kwargs)
