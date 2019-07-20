from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_view, name='main_view'),
    path('rater_form', views.rater_form, name='rater_form'),
    path('workflow_form', views.workflow_form, name='workflow_form'),
]
