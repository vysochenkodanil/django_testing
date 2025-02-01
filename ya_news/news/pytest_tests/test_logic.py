from http import HTTPStatus

import pytest
from django.urls import reverse
from news.models import Comment

FORM_DATA_TEMPLATE = {'text': 'Comment text'}


@pytest.mark.django_db
def test_anonymous_cannot_post_comment(client, news):
    news_detail_url = reverse('news:detail', args=[news.pk])
    form_data = FORM_DATA_TEMPLATE.copy()
    response = client.post(news_detail_url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND


@pytest.mark.django_db
def test_authenticated_can_post_comment(author_client, news):
    """
    Проверяет, что авторизованный пользователь
    может отправить комментарий.
    """
    news_detail_url = reverse('news:detail', args=[news.pk])
    form_data = FORM_DATA_TEMPLATE.copy()
    response = author_client.post(news_detail_url, data=form_data)

    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.filter(news=news, text=form_data['text']).exists()


@pytest.mark.django_db
def test_prohibited_words_in_comment(author_client, news):
    """
    Проверяет, что комментарий с
    запрещёнными словами не будет опубликован.
    """
    news_detail_url = reverse('news:detail', args=[news.pk])
    form_data = FORM_DATA_TEMPLATE.copy()
    form_data['text'] = 'Ты редиска!'
    response = author_client.post(news_detail_url, data=form_data)

    assert response.status_code == HTTPStatus.OK.value
    assert len(Comment.objects.filter(text=form_data['text'])) == 0
    assert 'Не ругайтесь!' in response.context['form'].errors['text']


@pytest.mark.django_db
def test_user_can_edit_own_comment(author_client, comment):
    """Проверяет, что пользователь может редактировать свои комментарии."""
    comment_edit_url = reverse('news:edit', kwargs={'pk': comment.pk})
    form_data = FORM_DATA_TEMPLATE.copy()
    form_data['text'] = 'Updated comment text'
    response = author_client.post(comment_edit_url, data=form_data)

    assert response.status_code == HTTPStatus.FOUND
    comment.refresh_from_db()
    assert comment.text == form_data['text']


@pytest.mark.django_db
def test_user_cannot_edit_others_comment(not_author_client, comment):
    """Проверяет, что пользователь не может редактировать чужие комментарии."""
    comment_edit_url = reverse('news:edit', kwargs={'pk': comment.pk})
    form_data = FORM_DATA_TEMPLATE.copy()
    form_data['text'] = 'Hacked comment text'
    response = not_author_client.post(comment_edit_url, data=form_data)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.filter(pk=comment.id).exists()


@pytest.mark.django_db
def test_user_can_delete_own_comment(author_client, comment):
    """Проверяет, что пользователь может удалять свои комментарии."""
    comment_delete_url = reverse('news:delete', kwargs={'pk': comment.pk})
    response = author_client.post(comment_delete_url)

    assert response.status_code == HTTPStatus.FOUND
    assert not Comment.objects.filter(pk=comment.pk).exists()


@pytest.mark.django_db
def test_user_cant_delete_comment(not_author_client, comment):
    """Проверяет, что пользователь не может удалять чужие комментарии."""
    comment_delete_url = reverse('news:delete', kwargs={'pk': comment.pk})
    response = not_author_client.post(comment_delete_url)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.filter(pk=comment.id).exists()
