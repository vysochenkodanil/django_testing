import pytest
from django.conf import settings
from django.urls import reverse


@pytest.mark.django_db
def test_news_count_on_homepage(client, news_list):
    """На главной странице не больше NEWS_COUNT_ON_HOME_PAGE новостей."""
    news_list()
    response = client.get(reverse('news:home'))
    print(response.context['object_list'])
    assert response.status_code == 200
    assert response.context['object_list'].count(
    ) == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order_on_homepage(client):
    """На главной странице новости отсортированы от свежей к старой."""
    response = client.get(reverse('news:home'))
    news_list_from_context = response.context['object_list']
    dates = [news.date for news in news_list_from_context]
    assert dates == sorted(dates, reverse=True)


@pytest.mark.django_db
def test_comment_order_on_detail_page(client, news, comments):
    """Комментарии на странице новости отсортированы по времени создания."""
    news_detail = reverse('news:detail', args=[news.pk])
    response = client.get(news_detail)
    comments = response.context['object'].comment_set.all()
    created_times = [comment.created for comment in comments]
    assert created_times == sorted(created_times)


@pytest.mark.django_db
def test_anonymous_user_sees_no_comment_form(client, news):
    """Анонимный пользователь не видит форму для комментариев."""
    news_detail = reverse('news:detail', args=[news.pk])
    response = client.get(news_detail)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authenticated_user_sees_comment_form(author_client, news):
    """Авторизованный пользователь видит форму для комментариев."""
    news_detail = reverse('news:detail', args=[news.pk])
    response = author_client.get(news_detail)
    assert 'form' in response.context
