from django.conf import settings
from django.contrib.auth import logout, views, forms
from django.core.paginator import Paginator
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views import generic
from django.views.decorators.http import require_GET
from django.urls import reverse_lazy

from .forms import AnswerForm, AskForm, QuestionSignUpForm, UserProfileForm
from .models import do_vote, Answer, Question, UserProfile


class IndexView(generic.TemplateView):
    template_name = 'questions/index.html'


class SearchView(generic.TemplateView):
    template_name = 'questions/search.html'


class QuestionsLoginView(views.LoginView):
    template_name = 'questions/login.html'
    redirect_field_name = 'next'
    authentication_form = forms.AuthenticationForm
    redirect_authenticated_user = True


class QuestionsSignUpView(generic.CreateView):
    form_class = QuestionSignUpForm
    success_url = reverse_lazy('questions:do_login')
    template_name = 'questions/signup.html'


def ask_question(request):
    if not request.user.id:
        return HttpResponseRedirect(reverse_lazy('questions:home'))
    if request.method == 'GET':
        return render(request, 'questions/ask.html', {'form': AskForm})
    if request.method == 'POST':
        question = Question.create_question(request)
        return HttpResponseRedirect(question.get_url())


def change_settings(request):
    if not request.user.id:
        return HttpResponseRedirect(reverse_lazy('questions:home'))

    if request.method == 'GET':
        return render(request, 'questions/settings.html', {})

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)

        if form.is_valid():
            user_profile = UserProfile.get_profile(user_id=request.user.id)
            user_profile.update_profile(request.POST.get("email"),
                                        request.FILES.get("avatar"))

        return render(request, 'questions/settings.html', {'form': form})


@require_GET
def do_logout(request):
    logout(request)
    redirect_url = request.META.get("HTTP_REFERER") \
        if request.META.get("HTTP_REFERER") else '/'
    return HttpResponseRedirect(redirect_url)


@require_GET
def do_user_vote(request):
    if request.GET.get("value"):
        q_or_a, id_, current_rating, up_or_down = request.GET.get("value").split()
        new_rating = do_vote(q_or_a, id_, request.user.id, up_or_down)
        return HttpResponse(new_rating)


def get_question_info(request, question_id):
    try:
        question = Question.objects.get(id=question_id)

    except Question.DoesNotExist:
        raise Http404

    if request.method == 'POST':
        Answer.create_answer(request, question)
        return HttpResponseRedirect(request.path)

    return render(request, 'questions/question.html',
                  {'question': question, 'form': AnswerForm})


@require_GET
def get_search_questions(request):
    search_query = request.GET.get("search").split()
    questions, page = Question.get_search_result(request, search_query)

    return HttpResponse(render_to_string('questions/search_render.html',
                                         {'questions': questions, 'page': page}))


@require_GET
def get_answers(request):
    answers, page, is_authenticated, right_one = \
        Answer.get_answers_page(request)

    return HttpResponse(render_to_string('questions/answers_render.html',
                                         {'answers': answers, 'page': page,
                                          'is_authenticated': is_authenticated,
                                          'right_one': right_one}))


@require_GET
def mark_answer(request):
    answer_id = request.GET.get('answer_id')
    is_right = request.GET.get('is_right')
    last_right_answer = Question.change_right_answer(answer_id, is_right)
    return HttpResponse(last_right_answer)


@require_GET
def paginate_data(request):
    """
    :param request: request with page and data parameters
    data == 'd' --> date values
    data == 't' --> trend values
    :return: render of html formatted data
    """
    paginate_by = request.GET.get('data')
    questions = Question.objects.order_by('-{by}'.format(
        by='pub_date' if paginate_by == 'd' else 'rating'))
    paginator = Paginator(questions, settings.BATCH_ON_PAGE)
    page = request.GET.get('page')

    if paginate_by == 'd':
        question_list_by_date = paginator.get_page(page)
        return HttpResponse(
            render_to_string('questions/date_list.html',
                             {'question_list_by_date': question_list_by_date,
                              'page': page}))
    else:
        question_list_by_trend = paginator.get_page(page)
        return HttpResponse(
            render_to_string('questions/trend_list.html',
                             {'question_list_by_trend': question_list_by_trend,
                              'page': page}))


@require_GET
def trending_data(_):
    """
    :return: render of html formatted data of top question by votes
    """
    question_list_by_trend = Question.get_trending_question()

    return HttpResponse(
        render_to_string('questions/trending.html',
                         {'question_list_by_trend': question_list_by_trend}))
