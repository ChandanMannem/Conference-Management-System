from django.urls import path
from . import views
from django.conf.urls import include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('paperview/<int:paperId>', views.paper_view_service, name='paperview'),
    path('signup/', views.signup, name='signup'),
    path('', include('django.contrib.auth.urls')),
    path('explore/', views.conference_view, name='explore'),
    path('conference/<slug:category>/', views.conference_view, name='conference'),
    path('conference/<slug:user_name>/<slug:category>/', views.conference_view, name='conference'),
    path('conference/<slug:user_name>/', views.conference_view, name='conference_user'),
    path('CreateData/', views.Create_data),
    path('conf_view/<int:confId>', views.conf_view, name='conf_view'),
    path('paperlist/<int:confId>', views.paper_list, name='paperlist')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
