import pytest
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from news.models import News, Comment


@pytest.mark.django_db
def test_news_count_on_homepage(client):
    """На главной странице не больше NEWS_COUNT_ON_HOME_PAGE новостей."""
    for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        News.objects.create(
            title=f'News {i}',
            text='News text',
            date=timezone.now()
        )
    response = client.get(reverse('news:home'))
    assert response.status_code == 200
    news_list = response.context['object_list']
    assert len(news_list) == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order_on_homepage(client):
    """На главной странице новости отсортированы от свежей к старой."""
    for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        News.objects.create(
            title=f'News {i}',
            text='News text',
            date=timezone.now() - timezone.timedelta(days=i)
        )
    response = client.get(reverse('news:home'))
    news_list = response.context['object_list']
    dates = [news.date for news in news_list]
    assert dates == sorted(dates, reverse=True)


@pytest.mark.django_db
def test_comment_order_on_detail_page(client, news_detail, news, author):
    """Комментарии на странице новости отсортированы по времени создания."""
    Comment.objects.bulk_create([
        Comment(
            news=news,
            author=author,
            text=f'Comment {i}',
            created=timezone.now() - timezone.timedelta(minutes=i)
        )
        for i in range(5)
    ])
    response = client.get(news_detail)
    comments = response.context['object'].comment_set.all()
    created_times = [comment.created for comment in comments]
    assert created_times == sorted(created_times)


@pytest.mark.django_db
def test_anonymous_user_sees_no_comment_form(client, news_detail):
    """Анонимный пользователь не видит форму для комментариев."""
    response = client.get(news_detail)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authenticated_user_sees_comment_form(author_client, news_detail):
    """Авторизованный пользователь видит форму для комментариев."""
    response = author_client.get(news_detail)
    assert 'form' in response.context
