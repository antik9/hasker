from django import forms as django_forms
from django.contrib.auth import forms as auth_forms
from django.contrib.auth.models import User


class AnswerForm(django_forms.Form):
    """
    Answer form include only textarea. Correctness of the field is
    length of symbols in it >= 10. Checks in jquery script.
    """
    text = django_forms.CharField(label='Text', max_length=2000,
                                  widget=django_forms.Textarea)


class AskForm(django_forms.Form):
    """
    Form consist of three fields: title, text and tags of new question
    """
    title = django_forms.CharField(label="Title", max_length=100)
    text = django_forms.CharField(label="Text", max_length=2000,
                                  widget=django_forms.Textarea)
    tags = django_forms.CharField(label="Tags", required=False)


class QuestionSignUpForm(auth_forms.UserCreationForm):
    """
    Expand UserCreationForm with email
    """
    email = django_forms.EmailField(label="e-mail")

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2',)


class UserProfileForm(django_forms.Form):
    """
    Simple form for User and his avatar
    """
    email = django_forms.EmailField(label="e-mail")
    avatar = django_forms.ImageField(label="avatar", required=False)
