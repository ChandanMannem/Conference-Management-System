from django.urls import path
from . import views

urlpatterns = [
    path('paperview/', views.paper_view_service),
]