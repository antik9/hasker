from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from questions import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='home'),
    path('login/', views.QuestionsLoginView.as_view(), name='do_login'),
    path('logout/', views.do_logout, name='do_logout'),
    path('rest/', include('api.urls')),
    path('signup/', views.QuestionsSignUpView.as_view(), name='signup'),
    path('settings/', views.change_settings, name='settings'),
    path('', include('questions.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR)