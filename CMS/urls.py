from django.urls import path
from . import views
from django.conf.urls import include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('paperview/<int:paperId>', views.paper_view_service, name='paperview'),
    path('signup/', views.signup, name='signup'),
    path('', include('django.contrib.auth.urls')),
    path('conferences/',  views.conferences_view, name='conferences'),
    path('conferences/<int:category>', views.conferences_view, name='conferences_category'),
    path('conferences/<str:past_conferences>', views.conferences_view, name='past_conferences'),
    path('conferences/<str:past_conferences>/<int:category>', views.conferences_view, name='past_conferences_category'),
    path('my_conferences/', views.user_conferences, name='user_conferences'),
    path('my_conferences/<int:category>', views.user_conferences, name='user_conferences_category'),
    path('my_conferences/<str:past_conferences>', views.conferences_view, name='past_user_conferences'),
    path('my_conferences/<str:past_conferences>/<int:category>', views.user_conferences, name='past_user_conferences_category'),
    path('error/', views.error, name='error'),
    path('CreateData/', views.Create_data),
    path('conf_view/<int:confId>', views.conf_view, name='conf_view'),
    path('paperlist/<int:confId>', views.paper_list, name='paperlist'),
    path('paper_redirect/<int:conf_id>',views.paper_redirect, name='paper_redirect'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
