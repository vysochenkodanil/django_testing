import pytest
from django.test.client import Client
from django.urls import reverse

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Author')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Not author')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    return News.objects.create(
        title='News title',
        text='News text',
    )


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Comment text'
    )


@pytest.fixture
def form_data():
    return {
        'text': 'Comment text'
    }


@pytest.fixture
def news_detail(news):
    return reverse('news:detail', args=[news.pk])


@pytest.fixture
def news_home():
    return reverse('news:home')


@pytest.fixture
def comment_edit(comment):
    return reverse('news:edit', kwargs={'pk': comment.pk})


@pytest.fixture
def comment_delete(comment):
    return reverse('news:delete', kwargs={'pk': comment.pk})


@pytest.fixture
def redirect_url_edit_comment(comment, login):
    url = reverse('news:edit', args=[comment.pk])
    return f'{login}?next={url}'


@pytest.fixture
def redirect_url_delete_comment(comment, login):
    url = reverse('news:delete', args=[comment.pk])
    return f'{login}?next={url}'


@pytest.fixture
def login():
    return reverse('users:login')


@pytest.fixture
def logout():
    return reverse('users:logout')


@pytest.fixture
def signup():
    return reverse('users:signup')
