from django import forms
from django.utils.safestring import mark_safe


class RangeSlider(forms.TextInput):
    def __init__(self, min_value, max_value, step, elem_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.min = str(min_value)
        self.max = str(max_value)
        self.step = str(step)
        self.elem_name = str(elem_name)

    def render(self, name, value, attrs=None, renderer=None):
        input_id = 'id_{}'.format(name)
        value = value if value else '0'
        html = """
        <input type="range" step="5" id="{}" name="{}" value="{}" data-rangeslider>
        <br>
        <h5><strong><output></output>%</strong></h5>
        """.format(input_id, name, value)
        return mark_safe(html)


class UrlItemWidget(forms.TextInput):
    def __init__(self, elem_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.elem_name = str(elem_name)

    def render(self, name, value, attrs=None, renderer=None):
        value_url = value
        html = """
        <h4><a target="_blank" href="{}">{}</a></h4>
        """.format(value_url, value)
        return mark_safe(html)


class ModelInitialTextWidget(forms.TextInput):
    def __init__(self, elem_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.elem_name = str(elem_name)

    def render(self, name, value, attrs=None, renderer=None):
        html = """
        <p>{}</p>
        """.format(value)
        return mark_safe(html)
