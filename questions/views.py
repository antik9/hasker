from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import logout, views, forms
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.views import generic
from django.views.decorators.http import require_GET
from django.urls import reverse_lazy

from .forms import AnswerForm, AskForm, QuestionSignUpForm, UserProfileForm
from .models import do_vote, Answer, Question, UserProfile


class IndexView(generic.TemplateView):
    """
    Template for home/index page of the Hasker
    """
    template_name = 'questions/index.html'


class SearchView(generic.TemplateView):
    """
    Template for search query. Search can be by tags or by words.
    """
    template_name = 'questions/search.html'


class QuestionsLoginView(views.LoginView):
    """
    View for Log In to the Hasker. If user is authenticated he/she
    automatically redirect to home page.
    """
    template_name = 'questions/login.html'
    redirect_field_name = 'next'
    authentication_form = forms.AuthenticationForm
    redirect_authenticated_user = True


class QuestionsSignUpView(generic.CreateView):
    """
    Singup View, in case of success user goes to login page.
    If there are errors in the form user stays on /signup/ and can
    see errors he or she has made.
    """
    form_class = QuestionSignUpForm
    success_url = reverse_lazy('do_login')
    template_name = 'questions/signup.html'


@login_required(redirect_field_name=reverse_lazy('home'), login_url=reverse_lazy('do_login'))
def ask_question(request):
    """
    :param request: HTTP request
    :return: if user is not authenticated redirect to login page
             in case of GET request user goes to /ask/ page
             in case of POST request user will be redirected to created
                question page
    """
    if request.method == 'GET':
        return render(request, 'questions/ask.html', {'form': AskForm})
    if request.method == 'POST':
        question = Question.create_question(request)
        return redirect(question.get_url())


@login_required(redirect_field_name=reverse_lazy('home'), login_url=reverse_lazy('do_login'))
def change_settings(request):
    """
    :param request: HTTP request
    :return: if user is not authenticated redirect to login page
             in case of GET request user goes to /settings/ page
             in case of POST request new settings will be applied and
                render in the form or errors will be rendered to the user
    """
    if request.method == 'GET':
        return render(request, 'questions/settings.html', {})

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)

        if form.is_valid():
            user_profile = UserProfile.get_profile(user_id=request.user.id)
            user_profile.update_profile(request.POST.get("email"),
                                        request.FILES.get("avatar"))
            return redirect(reverse_lazy('settings'))

        else:
            return render(request, 'questions/settings.html', {'form': form})


@require_GET
def do_logout(request):
    """
    :param request: HTTP request
    :return: redirect user to the page he or she comes from
    """
    logout(request)
    redirect_url = request.META.get("HTTP_REFERER") \
        if request.META.get("HTTP_REFERER") else '/'
    return redirect(redirect_url)


@require_GET
def do_user_vote(request):
    """
    :param request: HTTP async request
    :return: if user is authenticated
        (checks in jquery script for class .vote-btn-question)
        user can vote for a question or an answer asynchronously
    """
    if request.GET.get("value"):
        q_or_a, id_, current_rating, up_or_down = request.GET.get("value").split()

        # Check that user do not vote on his or her object
        new_rating = do_vote(q_or_a, id_, request.user.id, up_or_down)
        return HttpResponse(new_rating)


def error_404(_):
    """
    :return: Template page for every incorrect response and statuc code NOT FOUND
    """

    response = HttpResponse(render_to_string('questions/404.html', {}))
    response.status_code = HTTPStatus.NOT_FOUND.value
    return response


def get_question_info(request, question_id, question_enc):
    """
    :param request: HTTP request
    :param question_id:
    :return: 404 page if question does not exist
             page of a question if it's a GET request
             add new answer for a question in case of POST request
    """
    try:
        question = Question.objects.get(id=question_id)

    except Question.DoesNotExist:
        return error_404('')

    if request.method == 'POST':
        Answer.create_answer(request, question)
        return redirect(request.path)

    return render(request, 'questions/question.html',
                  {'question': question, 'form': AnswerForm})


@require_GET
def get_search_questions(request):
    """
    :param request: HTTP request async
    :return: HTTP response with rendered in html format content
            of <div> element with found questions
    """
    search_query = request.GET.get("search").split()
    questions, page = Question.get_search_result(request, search_query)

    return HttpResponse(render_to_string('questions/render/search_render.html',
                                         {'questions': questions, 'page': page}))


@require_GET
def get_answers(request):
    """
    :param request: HTTP request async
    :return: HTTP response with rendered in html format content
            of <div> element with new page of answers
    """
    answers, page, is_authenticated, right_one = \
        Answer.get_answers_page(request)

    return HttpResponse(render_to_string('questions/render/answers_render.html',
                                         {'answers': answers, 'page': page,
                                          'is_authenticated': is_authenticated,
                                          'right_one': right_one}))


@require_GET
def mark_answer(request):
    """
    :param request: HTTP request async
    :return: if user is author of a question he or she can mark with async
            request one answer as right one
    """
    answer_id = request.GET.get('answer_id')
    is_right = request.GET.get('is_right')
    last_right_answer = Question.change_right_answer(answer_id, is_right,
                                                     request.user.id)
    return HttpResponse(last_right_answer)


@require_GET
def paginate_data(request):
    """
    :param request: request with page and data parameters
            data == 'd' --> date values
            data == 't' --> trend values
    :return: HTTP response with rendered in html format content
            of <div> element
    """
    paginate_by = request.GET.get('data')

    # Get right sorting
    questions = Question.objects.order_by('-{by}'.format(
        by='pub_date' if paginate_by == 'd' else 'rating'))

    # Create Paginator
    paginator = Paginator(questions, settings.BATCH_ON_PAGE)
    page = request.GET.get('page')

    if paginate_by == 'd':
        question_list_by_date = paginator.get_page(page)
        return render(request, 'questions/render/date_list_render.html',
                      {'question_list_by_date': question_list_by_date,
                       'page': page})

    else:
        question_list_by_trend = paginator.get_page(page)
        return render(request, 'questions/render/trend_list_render.html',
                      {'question_list_by_trend': question_list_by_trend,
                       'page': page})


@require_GET
def trending_data(_):
    """
    :return: render of html formatted data of top question by votes
    """
    question_list_by_trend = Question.get_trending_question()

    return HttpResponse(
        render_to_string('questions/render/trending_render.html',
                         {'question_list_by_trend': question_list_by_trend}))
