from django.urls import path
from . import views

urlpatterns = [
    path('subscribe/', views.subscribe, name='subscribe'),
    path('verify/<uuid:verification_token>/', views.verify_email, name='verify_email'),
    path('unsubscribe/', views.unsubscribe, name='unsubscribe'),
    path('verify-unsubscribe/<uuid:verification_token>/', views.verify_unsubscribe, name='verify_unsubscribe'),
]