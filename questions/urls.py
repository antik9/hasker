from django.urls import path, re_path

from . import views

app_name = 'questions'

urlpatterns = [
    path('ask/', views.ask_question, name='ask'),
    path('static/', views.mark_answer, name='static_'),
    path('mark_right_answer/', views.mark_answer, name="mark_answer"),
    path('paginate_data/', views.paginate_data, name='paginate_data'),
    path('trending_data/', views.trending_data, name='trending_data'),
    path('login/', views.QuestionsLoginView.as_view(), name='do_login'),
    path('signup/', views.QuestionsSignUpView.as_view(), name='signup'),
    path('logout/', views.do_logout, name='do_logout'),
    path('vote/', views.do_user_vote, name='vote'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('get_answers/', views.get_answers, name='get_answers'),
    path('get_search/', views.get_search_questions, name='get_search'),
    path('settings/', views.change_settings, name='settings'),
    re_path(r'question/(?P<question_id>\d+)/.*\.html',
            views.get_question_info, name="question_info"),
    path('', views.IndexView.as_view(), name='home')
]
