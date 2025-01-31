import pytest
from http import HTTPStatus
from django.urls import reverse
from pytest_lazyfixture import lazy_fixture
from news.forms import CommentForm
from news.models import Comment


CLIENT = lazy_fixture('client')
AUTHOR_CLIENT = lazy_fixture('author_client')
NOT_AUTHOR_CLIENT = lazy_fixture('not_author_client')


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url, user, expected_status',
    (
        (lazy_fixture('news_home'), CLIENT, HTTPStatus.OK),
        (lazy_fixture('news_detail'), CLIENT, HTTPStatus.OK),
        (lazy_fixture('login'), CLIENT, HTTPStatus.OK),
        (lazy_fixture('logout'), CLIENT, HTTPStatus.OK),
        (lazy_fixture('signup'), CLIENT, HTTPStatus.OK),
        (lazy_fixture('comment_edit'), AUTHOR_CLIENT, HTTPStatus.OK),
        (
            lazy_fixture(
                'comment_edit'), NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND
        ),
        (lazy_fixture('comment_delete'), AUTHOR_CLIENT, HTTPStatus.OK),
    ),
)
def test_pages_availability_for_users(url, user, expected_status):
    """Проверяет доступность страниц для разных пользователей."""
    response = user.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url, user, expected_redirect',
    (
        (lazy_fixture('comment_edit'),
         CLIENT, lazy_fixture('redirect_url_edit_comment')),
        (lazy_fixture('comment_delete'),
         CLIENT, lazy_fixture('redirect_url_delete_comment')),
    ),
)
def test_redirects(url, user, expected_redirect):
    """Проверяет редиректы для анонимных пользователей."""
    response = user.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_redirect


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
