import pytest
from news.models import Comment
from http import HTTPStatus


@pytest.mark.django_db
def test_anonymous_cannot_post_comment(client, news_detail, form_data):
    """Проверяет, что анонимный пользователь не может отправить комментарий."""
    response = client.post(news_detail, data=form_data)
    assert response.status_code == 302


@pytest.mark.django_db
def test_authenticated_can_post_comment(
    author_client, news_detail, news, form_data
):
    """
    Проверяет, что авторизованный
    пользователь может отправить комментарий.
    """
    response = author_client.post(news_detail, data=form_data)

    assert response.status_code == 302
    assert Comment.objects.filter(news=news, text=form_data['text']).exists()


@pytest.mark.django_db
def test_prohibited_words_in_comment(author_client, news_detail, form_data):
    """
    Проверяет, что комментарий с
    запрещёнными словами не будет опубликован.
    """
    form_data['text'] = 'Ты редиска!'
    response = author_client.post(news_detail, data=form_data)
    assert response.status_code == 200
    assert Comment.objects.filter(text=form_data['text']).count() == 0
    assert 'Не ругайтесь!' in response.context['form'].errors['text']


@pytest.mark.django_db
def test_user_can_edit_own_comment(
    author_client, comment, form_data, comment_edit
):
    """Проверяет, что пользователь может редактировать свои комментарии."""
    form_data['text'] = 'Updated comment text'
    response = author_client.post(comment_edit, data=form_data)
    assert response.status_code == 302
    comment.refresh_from_db()
    assert comment.text == form_data['text']


@pytest.mark.django_db
def test_user_cannot_edit_others_comment(
    not_author_client, form_data, comment_edit, comment
):
    """Проверяет, что пользователь не может редактировать чужие комментарии."""
    form_data['text'] = 'Hacked comment text'
    response = not_author_client.post(comment_edit, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.filter(pk=comment.id).exists()


@pytest.mark.django_db
def test_user_can_delete_own_comment(author_client, comment, comment_delete):
    """Проверяет, что пользователь может удалять свои комментарии."""
    response = author_client.post(comment_delete)
    assert response.status_code == 302
    assert not Comment.objects.filter(pk=comment.pk).exists()


@pytest.mark.django_db
def test_user_cant_delete_comment(not_author_client, comment, comment_delete):
    """Проверяет, что пользователь не может удалять чужие комментарии."""
    response = not_author_client.post(comment_delete)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.filter(pk=comment.id).exists()
