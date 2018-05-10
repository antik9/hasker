import json

from http import HTTPStatus

from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.utils import timezone

from questions.models import Question, Tag


class HaskerApiTest(APITestCase):
    """
    Test correctness of api
        -> index
        -> trending
        -> answers
        -> question_info
        -> search
    """

    def setUp(self):
        """
        Set up consist of creating two users, two questions, vote and answer
        """
        self.user1 = User.objects.create_user(
            username='johndoe',
            email='johndoe@somemail.mail',
            password='nobodyknows')

        self.user2 = User.objects.create_user(
            username='averagejoe',
            email='joe@average.com',
            password='notsosimple')

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
            author=self.user2)

        self.client.login(username=self.user2.username, password='notsosimple')

        self.client.get(
            '/vote/', {'value': '{q_or_a} {id_} {current_rating} {up_or_down}'.format(
                q_or_a='q',
                id_=self.question1.id,
                current_rating=self.question1.rating,
                up_or_down='up')})

        self.client.post(self.question2.get_url(), {'Text': 'I got an answer'})

        response = self.client.post('/rest/api-token-auth/',
                                    {'username': self.user1.username,
                                     'password': 'nobodyknows'})

        self.token = response.data["token"]

    def test_answer(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT {}'.format(self.token))

        response = self.client.get(
            '/rest/answers/?question_id={}'.format(self.question2.id)
        )

        json_response = json.loads(response._container[0].decode('utf-8'))["answers"]
        self.assertEqual(len(json_response), 1)
        self.assertEqual(json_response[0]["answer_text"], "I got an answer")

    def test_bad_auth(self):
        # Answers page
        response = self.client.get(
            '/rest/answers/?question_id={}'.format(self.question2.id))
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

        # Question page
        response = self.client.get(
            '/rest/question/?question_id={}'.format(self.question1.id)
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

        # Search
        response = self.client.get('/rest/search/?search=title')
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_batch(self):
        response = self.client.get('/rest/index/?batch=1')

        json_response = json.loads(response._container[0].decode('utf-8'))["questions"]
        self.assertEqual(len(json_response), 1)
        self.assertEqual(json_response[0]["id"], self.question1.id)

    def test_index_by_date(self):
        response = self.client.get('/rest/index/?data=d')

        json_response = json.loads(response._container[0].decode('utf-8'))["questions"]
        self.assertEqual(len(json_response), 2)
        self.assertEqual(json_response[0]["id"], self.question2.id)

    def test_index_by_rating(self):
        response = self.client.get('/rest/index/?data=t')

        json_response = json.loads(response._container[0].decode('utf-8'))["questions"]
        self.assertEqual(len(json_response), 2)
        self.assertEqual(json_response[0]["id"], self.question1.id)

    def test_page(self):
        response = self.client.get('/rest/index/?batch=1&page=2')

        json_response = json.loads(response._container[0].decode('utf-8'))["questions"]
        self.assertEqual(len(json_response), 1)
        self.assertEqual(json_response[0]["id"], self.question2.id)

    def test_question_info(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT {}'.format(self.token))

        response = self.client.get(
            '/rest/question/?question_id={}'.format(self.question1.id)
        )

        json_response = json.loads(response.content.decode('utf-8'))
        self.assertEqual(json_response["question_text"], self.question1.question_text)
        self.assertEqual(json_response["rating"], 1)

    def test_search_by_tag(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT {}'.format(self.token))
        response = self.client.get('/rest/search/?search=tag:move')

        json_response = json.loads(response._container[0].decode('utf-8'))["questions"]
        self.assertEqual(len(json_response), 1)
        self.assertEqual(json_response[0]["id"], self.question1.id)

    def test_search_by_word(self):
        self.client.credentials(HTTP_AUTHORIZATION='JWT {}'.format(self.token))
        response = self.client.get('/rest/search/?search=title')

        json_response = json.loads(response._container[0].decode('utf-8'))["questions"]
        self.assertEqual(len(json_response), 2)
        self.assertEqual(json_response[0]["id"], self.question1.id)

    def test_trending(self):
        response = self.client.get('/rest/trending/')

        json_response = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(json_response), 2)
        self.assertEqual(json_response[0]["id"], self.question1.id)
