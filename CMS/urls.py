from django.urls import path
from . import views
from django.conf.urls import include

urlpatterns = [
    path('paperview/', views.paper_view_service),
    path('signup/', views.signup, name='signup'),
    path('', include('django.contrib.auth.urls')),
    path('explore/', views.conference_view, name='explore'),
    path('conference/<slug:category>/', views.conference_view, name='conference'),
    path('conference/<slug:user_name>/<slug:category>/', views.conference_view, name='conference'),
    path('conference/<slug:user_name>/', views.conference_view, name='conference_user'),
    path('CreateData/', views.Create_data)
]
