from django.urls import path
from . import views

urlpatterns = [
    path('subscribe/', views.subscribe, name='subscribe'),
    path('verify/<uuid:verification_token>/', views.verify_email, name='verify_email'),
]