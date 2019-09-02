from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_view, name='main_view'),
    path('sign_in', views.sign_in, name='sign_in'),
    path('logout', views.logout, name='logout'),
    path('sign_up', views.sign_up, name='sign_up'),
    path('workflow_form', views.workflow_form, name='workflow_form'),
]
