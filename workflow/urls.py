from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_view, name='main_view'),
    path('sign_in', views.sign_in, name='sign_in'),
    path('logout', views.logout, name='logout'),
    path('sign_up', views.sign_up, name='sign_up'),
    path('workflow_form', views.workflow_form, name='workflow_form'),
    path('previous_item', views.previous_item, name='previous_item'),
    path('mturk_register', views.MTurkRegister.as_view(), name='mturk_register'),
    path('mturk_demographics', views.MTurkDemographics.as_view(), name='mturk_demographics'),
    path('mturk_label', views.MTurkLabel.as_view(), name='mturk_label'),
]
