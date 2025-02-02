from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_lazyfixture import lazy_fixture

from news.forms import CommentForm
from news.models import Comment

CLIENT = lazy_fixture('client')
AUTHOR_CLIENT = lazy_fixture('author_client')
NOT_AUTHOR_CLIENT = lazy_fixture('not_author_client')


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url_name, user, expected_status',
    (
        ('news:home', CLIENT, HTTPStatus.OK),
        ('news:detail', CLIENT, HTTPStatus.OK),
        ('users:login', CLIENT, HTTPStatus.OK),
        ('users:logout', CLIENT, HTTPStatus.OK),
        ('users:signup', CLIENT, HTTPStatus.OK),
        ('news:edit', AUTHOR_CLIENT, HTTPStatus.OK),
        ('news:edit', NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND),
        ('news:delete', AUTHOR_CLIENT, HTTPStatus.OK),
    ),
)
def test_pages_availability_for_users(
        url_name, user, expected_status, news, comment):
    """Проверяет доступность страниц для разных пользователей."""
    if url_name in ('news:detail', 'news:edit', 'news:delete'):
        if url_name == 'news:detail':
            url = reverse(url_name, kwargs={'pk': news.pk})
        else:
            url = reverse(url_name, kwargs={'pk': comment.pk})
    else:
        url = reverse(url_name)
    response = user.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url_name, user, expected_redirect',
    (
        ('news:edit', CLIENT, 'users:login'),
        ('news:delete', CLIENT, 'users:login'),
    ),
)
def test_redirects(url_name, user, expected_redirect, comment):
    """Проверяет редиректы для анонимных пользователей."""
    url = reverse(url_name, kwargs={'pk': comment.pk})
    login_url = reverse(expected_redirect)
    expected_url = f"{login_url}?next={url}"
    response = user.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_url


@pytest.mark.django_db
def test_news_detail_context(client, news):
    """Проверяет контекст страницы деталей новости."""
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.get(url)
    assert 'news' in response.context
    assert response.context['news'] == news


@pytest.mark.django_db
def test_comment_form_in_context(author_client, news):
    """
    Проверяет, что форма комментария есть в
    контексте для авторизованного пользователя.
    """
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)


@pytest.mark.django_db
def test_comment_creation(author_client, news):
    """Проверяет создание комментария авторизованным пользователем."""
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = author_client.post(url, data={'text': 'New Comment'})
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.filter(news=news, text='New Comment').exists()
