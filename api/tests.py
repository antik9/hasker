from django.test import TestCase

from rest_framework import authentication
from rest_framework.response import Response
from rest_framework.views import APIView


# Create your tests here.
# class SecretView(APIView):
#     authentication_classes = (authentication.TokenAuthentication,)
#
#     def get(self, request):
#         return Response("Success")
