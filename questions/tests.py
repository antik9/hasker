from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from .models import Answer, Question, Tag


class GETAnonymousTest(TestCase):
    """
    Class for test available GET requests for unauthorized user.
    Test correctness of render:
        -> index
        -> login
        -> signup
        -> search
    """

    def test_index(self):
        response = self.client.get('/')

        self.assertContains(response, 'Hasker', html=True)
        self.assertContains(response, 'Sign up', html=True)
        self.assertContains(response, 'Log in', html=True)
        self.assertContains(response, 'Trending', html=True)

    def test_login(self):
        response = self.client.get('/login/')

        self.assertContains(response, 'Hasker', html=True)
        self.assertContains(response, 'LOG IN', html=True)
        self.assertContains(response, 'Username', html=True)
        self.assertContains(response, 'Password', html=True)

    def test_signup(self):
        response = self.client.get('/signup/')

        self.assertContains(response, 'Hasker', html=True)
        self.assertContains(response, 'SIGN UP', html=True)
        self.assertContains(response, 'e-mail', html=True)
        self.assertContains(response, 'Password confirmation', html=True)

    def test_search(self):
        response = self.client.get('/search/?search=something')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_404(self):
        response = self.client.get('/abcdefgh/')
        self.assertEqual(response.status_code, 404)


class POSTAnonymousTest(TestCase):
    """
    Class for test available POST requests for unauthorized user.
    Test correctness of post request:
        -> login
        -> signup
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username='johndoe',
            email='johndoe@somemail.mail',
            password='nobodyknows')

    def test_signup(self):
        response = self.client.post('/signup/', {'username': 'averagejoe',
                                                 'password1': 'notsosimple',
                                                 'password2': 'notsosimple',
                                                 'email': 'joe@average.com'})

        self.assertRedirects(response, '/login/')
        self.assertTrue(User.objects.get(username='averagejoe'))

    def test_login(self):
        response = self.client.post('/login/', {'username': self.user.username,
                                                'password': 'nobodyknows'})

        self.assertRedirects(response, '/')

    # Not available for anonymous user, redirect him to login page
    def test_ask(self):
        response = self.client.post('/ask/', {'title': 'some title',
                                              'text': 'nobody knows this text'})

        self.assertRedirects(response, '/login/?/=/ask/')


class GETAuthorizedTest(TestCase):
    """
    Class for test available GET requests for authorized user.
    Test correctness of render:
        -> ask
        -> settings
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username='johndoe',
            email='johndoe@somemail.mail',
            password='nobodyknows')

        self.client.login(username='johndoe', password='nobodyknows')

    def test_ask(self):
        response = self.client.get('/ask/')

        self.assertEqual(response.status_code, HTTPStatus.OK.value)
        self.assertContains(response, 'Hasker', html=True)
        self.assertContains(response, 'ASK A QUESTION', html=True)
        self.assertContains(response, 'Tags', html=True)

    def test_settings(self):
        response = self.client.get('/settings/')

        self.assertEqual(response.status_code, HTTPStatus.OK.value)
        self.assertContains(response, 'Hasker', html=True)
        self.assertContains(response, 'SETTINGS', html=True)
        self.assertContains(response, 'Avatar', html=True)


class POSTAuthorizedTestSimple(TestCase):
    """
    Class for test available POST requests for authorized user.
    Test correctness of render:
        -> ask
        -> settings
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username='johndoe',
            email='johndoe@somemail.mail',
            password='nobodyknows')

        self.client.login(username='johndoe', password='nobodyknows')

    def test_ask(self):
        response = self.client.post('/ask/', {'title': 'some title',
                                              'text': 'nobody knows this text',
                                              'tags': 'tag1, tag2'})

        self.assertEqual(Question.objects.count(), 1)
        self.assertRedirects(response, Question.objects.all()[0].get_url())

    def test_settings(self):
        response = self.client.post('/settings/', {'email': 'lol@lol.lol'})

        self.assertEqual(User.objects.get(username=self.user.username).email,
                         'lol@lol.lol')

        self.assertRedirects(response, '/settings/')


class POSTAuthorizedWithQuestionsTest(TestCase):
    """
    Class for test available POST requests for authorized user.
    Test correctness of render:
        -> answer
        -> vote for question
        -> vote for an answer
        -> mark right question
    """

    def setUp(self):
        self.user1 = User.objects.create_user(
            username='johndoe',
            email='johndoe@somemail.mail',
            password='nobodyknows')

        self.user2 = User.objects.create_user(
            username='averagejoe',
            email='joe@average.com',
            password='notsosimple')

        self.question = Question.objects.create(
            question_title='Simple title',
            question_text='Blah blah blah one two three',
            pub_date=timezone.now(),
            author=self.user1)

        self.answer = Answer.objects.create(
            answer_text='Doo roo ran ron',
            related_question=self.question,
            pub_date=timezone.now(),
            author=self.user1)

    def test_answer(self):
        self.client.login(username=self.user2.username, password='notsosimple')
        response = self.client.post(self.question.get_url(), {'Text': 'I got an answer'})

        self.assertEqual(Answer.objects.count(), 2)
        self.assertRedirects(response, self.question.get_url())

        response = self.client.get('/get_answers/', {'question_id': self.question.id})
        self.assertContains(response, 'I got an answer')

    def test_vote_for_own_question(self):
        self.client.login(username=self.user1.username, password='nobodyknows')

        response = self.client.get(
            '/vote/', {'value': '{q_or_a} {id_} {current_rating} {up_or_down}'.format(
                q_or_a='q',
                id_=self.question.id,
                current_rating=self.question.rating,
                up_or_down='up')})

        self.assertEqual(Question.objects.all()[0].rating, 0)
        self.assertContains(response, 'None')

    def test_vote_for_another_user_question(self):
        self.client.login(username=self.user2.username, password='notsosimple')

        response = self.client.get(
            '/vote/', {'value': '{q_or_a} {id_} {current_rating} {up_or_down}'.format(
                q_or_a='q',
                id_=self.question.id,
                current_rating=self.question.rating,
                up_or_down='up')})

        self.assertEqual(Question.objects.all()[0].rating, 1)
        self.assertContains(response, str(self.question.rating + 1))

    def test_vote_for_own_answer(self):
        self.client.login(username=self.user1.username, password='nobodyknows')

        response = self.client.get(
            '/vote/', {'value': '{q_or_a} {id_} {current_rating} {up_or_down}'.format(
                q_or_a='a',
                id_=self.answer.id,
                current_rating=self.answer.rating,
                up_or_down='up')})

        self.assertEqual(Answer.objects.all()[0].rating, 0)
        self.assertContains(response, 'None')

    def test_vote_for_another_user_answer(self):
        self.client.login(username=self.user2.username, password='notsosimple')

        response = self.client.get(
            '/vote/', {'value': '{q_or_a} {id_} {current_rating} {up_or_down}'.format(
                q_or_a='a',
                id_=self.answer.id,
                current_rating=self.answer.rating,
                up_or_down='up')})

        self.assertEqual(Answer.objects.all()[0].rating, 1)
        self.assertContains(response, str(self.answer.rating + 1))

    def test_hack_mark_answer(self):
        self.client.login(username=self.user2.username, password='notsosimple')

        response = self.client.get(
            '/mark_right_answer/', {'answer_id': self.answer.id,
                                    'is_right': 'true' if self.answer.right else 'false'})

        self.assertFalse(Answer.objects.all()[0].right)
        self.assertContains(response, 'None')

    def test_correct_mark_answer(self):
        self.client.login(username=self.user1.username, password='nobodyknows')

        self.client.get(
            '/mark_right_answer/', {'answer_id': self.answer.id,
                                    'is_right': 'true' if self.answer.right else 'false'})

        self.assertTrue(Answer.objects.all()[0].right)


class RendererTest(TestCase):
    """
    Class for test available GET requests for rendered html
    Test correctness of render:
        -> trending
        -> trend list on index
        -> date list on index
        -> search render for words
        -> search render for tags
    """

    def setUp(self):
        self.user1 = User.objects.create_user(
            username='johndoe',
            email='johndoe@somemail.mail',
            password='nobodyknows')

        self.tag = Tag.objects.create(tag_text='move')

        self.question1 = Question.objects.create(
            question_title='Simple title',
            question_text='Blah blah blah one two three',
            pub_date=timezone.now(),
            author=self.user1)

        self.question1.question_tags.add(self.tag)
        self.question1.save()

        self.question2 = Question.objects.create(
            question_title='Intriguing title',
            question_text='four five six',
            pub_date=timezone.now(),
            author=self.user1)

    def test_trending(self):
        response = self.client.get('/trending_data/')

        self.assertContains(response, self.question1.question_title)
        self.assertContains(response, self.question2.question_title)

    def test_trend_pagination(self):
        response = self.client.get('/paginate_data/', {'data': 't', 'page': 1})

        self.assertContains(response, self.question1.question_title)
        self.assertContains(response, self.question2.question_title)

    def test_date_pagination(self):
        response = self.client.get('/paginate_data/', {'data': 'd', 'page': 1})

        self.assertContains(response, self.question1.question_title)
        self.assertContains(response, self.question2.question_title)

    def test_search_by_word(self):
        response = self.client.get('/get_search/?search=title')

        self.assertContains(response, self.question1.question_title)
        self.assertContains(response, self.question2.question_title)

    def test_search_by_tag(self):
        response = self.client.get('/get_search/?search=tag:{tag}'.format(tag=self.tag))

        self.assertContains(response, self.question1.question_title)
        self.assertNotContains(response, self.question2.question_title)
