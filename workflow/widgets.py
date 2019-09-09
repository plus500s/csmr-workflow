from django import forms
from django.utils.safestring import mark_safe


class RangeSlider(forms.TextInput):
    def __init__(self, min, max, step, elem_name, *args, **kwargs):  # noqa
        super().__init__(*args, **kwargs)
        self.min = str(min)
        self.max = str(max)
        self.step = str(step)
        self.elem_name = str(elem_name)

    def render(self, name, value, attrs=None, renderer=None):
        input_id = 'id_{}'.format(name)
        value = value if value else '0'
        html = """
        <input type="range" step="5" id="{}" name="{}" value="{}" data-rangeslider>
        <h4><output></output>%</h4>
        """.format(input_id, name, value)
        return mark_safe(html)
