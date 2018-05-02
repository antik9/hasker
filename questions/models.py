import datetime
from urllib.parse import quote

from django.conf import settings
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.core.mail import EmailMultiAlternatives
from django.db import models, transaction
from django.utils import timezone

email_template = "<p>You get a new answer to your question:</p> " \
                 "<p><b>{question_text}</p></b><br>" \
                 "<p>You can go by this link and read an answer:<p>" \
                 "<p><a><i>{link}</i></a></p><br>" \
                 "<p>Hasker©</p><br>"


class UserProfile(models.Model):
    """
    Profile expand user data with avatar image
    """
    user = models.OneToOneField(to=User,
                                on_delete=models.CASCADE,
                                null=False, blank=False)
    avatar = models.ImageField(upload_to="static/user/images", null=True)

    @staticmethod
    def get_profile(user_id):
        try:
            return UserProfile.objects.get(user_id=user_id)
        except UserProfile.DoesNotExist:
            return UserProfile.objects.create(user_id=user_id)

    def update_profile(self, email, avatar):

        with transaction.atomic():
            if self.user.email != email:
                self.user.email = email
                self.user.save()

            if avatar:
                self.avatar = avatar
                self.save()


class Tag(models.Model):
    """
    Tag is common topic with which question is associated.
    One question can have zero, one or more tags.
    """
    tag_text = models.CharField(max_length=30)

    def __str__(self):
        return self.tag_text


class Question(models.Model):
    """
    Question is the model of questions in hasker.
    The question should have its own author, title, text and published date.
    Also question has optional tags to associate it with category of
    similar questions.
    """

    question_title = models.CharField(max_length=100, null=False, blank=False)
    question_text = models.CharField(max_length=2000, null=False, blank=False)
    pub_date = models.DateTimeField('date published', null=False, blank=False)

    question_tags = models.ManyToManyField(to=Tag, blank=False)

    author = models.ForeignKey(to=User, on_delete=models.DO_NOTHING,
                               null=False, blank=False)

    rating = models.IntegerField(null=False, blank=False, default=0)

    def __str__(self):
        return self.question_title

    def get_url(self):
        return "/question/" + str(self.id) + "/" + \
               quote("-".join(self.question_title.split())) + ".html"

    def get_tags(self):
        return self.question_tags.all()

    def get_avatar(self):
        avatar = UserProfile.get_profile(self.author.id).avatar
        if avatar:
            return '/' + avatar.url

    @staticmethod
    def get_trending_question():
        question_list = Question.objects.order_by('-rating').all()
        return question_list[:settings.TRENDING_BATCH]

    @staticmethod
    def create_question(request):
        with transaction.atomic():

            new_question = Question.objects.create(
                author=request.user,
                question_title=request.POST.get("title"),
                question_text=request.POST.get("text"),
                pub_date=datetime.datetime.now()
            )

            tags = set(map(lambda tag: tag.strip(),
                           request.POST.get("tags").split(",")))

            for tag_text in tags:
                if tag_text:
                    try:
                        tag = Tag.objects.get(tag_text=tag_text)
                    except Tag.DoesNotExist:
                        tag = Tag.objects.create(tag_text=tag_text)
                    new_question.question_tags.add(tag)

            new_question.save()

            return new_question

    @staticmethod
    def get_search_result(request, search_query):
        questions = Question.objects.all()
        page = request.GET.get('page')
        if search_query[0][:4] == "tag:":
            search_query = search_query[0].split(':')[1]
            try:
                tag = Tag.objects.get(tag_text=search_query).id
                questions = questions.filter(question_tags=tag)
            except Tag.DoesNotExist:
                questions = None

        else:
            for word in search_query:
                questions = questions.filter(models.Q(question_title__icontains=word) |
                                             models.Q(question_text__icontains=word))

        if questions:
            questions = questions.order_by('-rating', '-pub_date')
            paginator = Paginator(questions, settings.SEARCH_BATCH)
            if not page:
                page = 1
            questions = paginator.get_page(page)

        return questions, page

    @staticmethod
    def change_right_answer(answer_id, is_right):
        try:
            with transaction.atomic():
                answer = Answer.objects.get(id=answer_id)
                is_right = False if is_right == 'false' else True

                right_answer = None

                if not is_right:
                    right_answer = Answer.objects.all().filter(
                        related_question=answer.related_question)
                    right_answer = right_answer.filter(right=True)

                    if right_answer:
                        right_answer = right_answer[0]
                        right_answer.right = False
                        right_answer.save()

                answer.right = not is_right
                answer.save()

                return right_answer.id if right_answer else None

        except Answer.DoesNotExist:
            pass

    def was_published_ago(self):
        """
        :return: string with format 'asked 10 minutes ago' for current question
        with appropriate time delta
        """
        template_ago = "asked {delta:.0f} {interval}{plural} ago"
        delta = datetime.datetime.now(tz=timezone.utc) - self.pub_date

        def print_date(divisor, interval):
            return template_ago.format(
                delta=delta.total_seconds() // divisor,
                interval=interval,
                plural='' if delta.total_seconds() // divisor == 1 else 's')

        if delta < datetime.timedelta(hours=1):
            return print_date(60, 'minute')

        if delta < datetime.timedelta(days=1):
            return print_date(60 * 60, 'hour')

        if delta < datetime.timedelta(days=366):
            return print_date(60 * 60 * 24, 'day')

        return print_date(60 * 60 * 24 * 365, 'year')


class Answer(models.Model):
    """
    One question can have zero, on or more answers.
    Each answer has votes.
    One user can vote only once for each answer in selected question.
    Only one answer for selected question can have flag - right answer.
    """

    answer_text = models.CharField(max_length=2000, null=False, blank=False)
    pub_date = models.DateTimeField("date published", null=False, blank=False)
    right = models.BooleanField("is right answer", null=False, blank=False,
                                default=False)

    related_question = models.ForeignKey(to=Question, null=False, blank=False,
                                         on_delete=models.CASCADE)

    author = models.ForeignKey(to=User, on_delete=models.DO_NOTHING,
                               null=False, blank=False)

    rating = models.IntegerField(null=False, blank=False, default=0)

    def __str__(self):
        return self.answer_text

    @staticmethod
    def create_answer(request, question):
        Answer.objects.create(
            answer_text=request.POST.get('Text'),
            related_question=question,
            author=request.user,
            pub_date=datetime.datetime.now()
        )

        if settings.EMAIL_HOST_USER:
            subject, from_email, to = "You get an answer to your question", \
                                      'noreply@hasker.com', question.author.email
            text_content = ''
            html_content = email_template.format(
                question_text=question.question_text,
                link=settings.BASE_URL + question.get_url())

            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

    @staticmethod
    def get_answers_page(request):
        question_id = request.GET.get("question_id")
        page = request.GET.get("page")
        is_authenticated = request.GET.get('is_authenticated', False)

        if not page:
            page = 1
        answers = Answer.objects.filter(
            related_question_id=question_id).order_by('-rating')

        paginator = Paginator(answers, settings.ANSWERS_BATCH)
        answers = paginator.get_page(page)

        right_one = None
        for answer in answers:
            if answer.right:
                right_one = answer.id

        return answers, page, is_authenticated, right_one

    def get_avatar(self):
        avatar = UserProfile.get_profile(self.author.id).avatar
        if avatar:
            return '/' + avatar.url


class VoteQuestion(models.Model):
    """
    Each question can have votes.
    Only one vote for one user for each question is available.
    """
    voter = models.ForeignKey(to=User, on_delete=models.DO_NOTHING,
                              null=False, blank=False)

    text_field = models.ForeignKey(to=Question, on_delete=models.CASCADE,
                                   null=False, blank=False)

    up = models.BooleanField(null=False, blank=True, default=False)
    down = models.BooleanField(null=False, blank=True, default=False)


class VoteAnswer(models.Model):
    """
    Each answer to question can have votes.
    Only one vote for one user for each answer is available.
    """
    voter = models.ForeignKey(to=User, on_delete=models.DO_NOTHING,
                              null=False, blank=False)

    text_field = models.ForeignKey(to=Answer, on_delete=models.CASCADE,
                                   null=False, blank=False)

    up = models.BooleanField(null=False, blank=True, default=False)
    down = models.BooleanField(null=False, blank=True, default=False)


def do_vote(question_or_answer, text_object_id, user_id, vote_status):
    """
    :param question_or_answer: class of object
    :param text_object_id: id of answer or question
    :param user_id:
    :param vote_status: up or down
    """
    object_class = VoteQuestion if question_or_answer == 'q' else VoteAnswer
    result = None

    try:
        current_object = object_class.objects.get(
            voter_id=user_id, text_field_id=text_object_id)
    except (VoteQuestion.DoesNotExist, VoteAnswer.DoesNotExist):
        current_object = None

    if not current_object:
        current_object = object_class.objects.create(
            voter_id=user_id, text_field_id=text_object_id)

    for value, reverse_value in (('up', 'down'), ('down', 'up')):
        # Do nothing if voice is already equal to new status
        if vote_status == value and not current_object.__dict__.get(value):
            if current_object.__dict__.get(reverse_value):
                current_object.__dict__[reverse_value] = False
            else:
                current_object.__dict__[value] = True
            result = update_rating(question_or_answer, text_object_id, value)
            current_object.save()

    return result


def update_rating(question_or_answer, text_object_id, up_or_down):
    """
    :param question_or_answer: class of object
    :param text_object_id: id of answer or question
    :param up_or_down: vote up or vote down for object
    :return: new rating of an object
    """
    object_class = Question if question_or_answer == 'q' else Answer
    current_object = object_class.objects.get(id=text_object_id)
    current_object.rating += 1 if up_or_down == "up" else -1
    current_object.save()
    return current_object.rating
