from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.utils import timezone

from news.models import Comment, News


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
def news_list():
    News.objects.bulk_create(
        News(title=f'News number {index}',
             text='News text',
             date=datetime.today() - timedelta(days=index)
             )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )

@pytest.fixture
def comments(news, author):
    return Comment.objects.bulk_create([
        Comment(
            news=news,
            author=author,
            text=f'Comment {i}',
            created=timezone.now() - timezone.timedelta(minutes=i)
        )
        for i in range(5)
    ])
