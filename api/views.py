import json

from http import HTTPStatus

from django.core.paginator import Paginator
from django.http import HttpResponse
from django.views.decorators.http import require_GET

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .serializers import AnswerSerializer, QuestionSerializer, \
    QuestionBatchSerializer, QuestionTrendingSerializer

from questions.models import Answer, Question

# Get Help from README and returns it on /rest/ uri and
# all uris with prefix /rest/ that are not present in api/urls.py

with open('api/README.md') as readme:
    API_HELP = readme.read()


# ********************* HANDLERS **********************#

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_api_answers(request):
    """
    :param request: HTTP request
    :return: one page with answers to the question in json format
    """
    question_id = request.GET.get('question_id')
    if not question_id:
        return HttpResponse(content=json.dumps({"error": "no id in request"}),
                            status=HTTPStatus.BAD_REQUEST)

    answers, page, *_ = Answer.get_answers_page(request)
    serialized_answers = AnswerSerializer(answers, many=True)
    return HttpResponse(
        json.dumps({
            "question_id": question_id,
            "page": page,
            'has next': answers.has_next(),
            'has prev': answers.has_previous(),
            "answers": serialized_answers.data}, indent=4))


@require_GET
def get_api_index(request):
    """
    :param request: HTTP request
    :return: one page with questions sorted by date or rating in json format
    """
    paginate_by = request.GET.get('data', 't')
    batch = request.GET.get('batch', 10)
    page = request.GET.get('page', 1)

    # Get right sorting
    questions = Question.objects.order_by('-{by}'.format(
        by='pub_date' if paginate_by == 'd' else 'rating'))

    # Create Paginator
    paginator = Paginator(questions, batch)
    questions = paginator.get_page(page)

    questions_serialized = QuestionBatchSerializer(questions, many=True)

    return HttpResponse(
        json.dumps({
            'page': questions.number,
            'sort by': 'date' if paginate_by == 'd' else 'rating',
            'has next': questions.has_next(),
            'has prev': questions.has_previous(),
            'questions': questions_serialized.data,
        }, indent=4))


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_api_question(request):
    """
    :param request: HTTP request
    :return: full information about a question in json format
    """
    question_id = request.GET.get('question_id')
    if not question_id:
        return HttpResponse(content=json.dumps({"error": "no id in request"}),
                            status=HTTPStatus.BAD_REQUEST)

    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return HttpResponse(content=json.dumps({"error": "no question with this id"}),
                            status=HTTPStatus.NOT_FOUND)

    return HttpResponse(json.dumps(QuestionSerializer(question).data, indent=4))


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_api_search(request):
    """
    :param request: HTTP request
    :return: one page with found questions in json format
    """
    search_query = request.GET.get("search")

    if not search_query:
        return HttpResponse(content=json.dumps({"error": "empty search query"}),
                            status=HTTPStatus.BAD_REQUEST)

    search_query = search_query.split()
    questions, page = Question.get_search_result(request, search_query)

    questions_serialized = QuestionBatchSerializer(questions, many=True)

    return HttpResponse(
        json.dumps({
            'page': page,
            'has next': questions.has_next() if questions else None,
            'has prev': questions.has_previous() if questions else None,
            'questions': questions_serialized.data,
        }, indent=4))


@require_GET
def get_api_trending(_):
    """
    :return: top 5 questions by rating in json format
    """

    questions = Question.get_trending_question()
    serialized_questions = QuestionTrendingSerializer(questions, many=True)
    return HttpResponse(json.dumps(serialized_questions.data, indent=4))


@require_GET
def get_api_help(_):
    """
    :return: README
    """
    return HttpResponse(API_HELP)
