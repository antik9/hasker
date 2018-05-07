from django.urls import path, re_path

from . import views

app_name = 'questions'

urlpatterns = [
    path('ask/', views.ask_question, name='ask'),
    path('get_answers/', views.get_answers, name='get_answers'),
    path('get_search/', views.get_search_questions, name='get_search'),
    path('mark_right_answer/', views.mark_answer, name="mark_answer"),
    path('paginate_data/', views.paginate_data, name='paginate_data'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('trending_data/', views.trending_data, name='trending_data'),
    path('vote/', views.do_user_vote, name='vote'),

    re_path(r'question/(?P<question_id>\d+)/(?P<question_enc>.*)\.html',
            views.get_question_info, name="question_info"),
    re_path(r'.*', views.error_404, name='not_found'),
]
