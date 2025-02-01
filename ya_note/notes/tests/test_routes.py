from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class BaseTest(TestCase):
    """Базовый класс для тестов, содержащий общие данные и методы."""

    HOME_URL = reverse('notes:home')
    ADD_URL = reverse('notes:add')
    LIST_URL = reverse('notes:list')
    SUCCESS_URL = reverse('notes:success')

    @classmethod
    def setUpTestData(cls):
        """Создает тестовые данные для всех тестов."""
        cls.author = User.objects.create(username='Автор заметки')
        cls.note = Note.objects.create(
            title='Заголовок заметки',
            text='Текст заметки',
            slug='test-slug',
            author=cls.author
        )
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))


class TestHomePage(BaseTest):
    """Тесты для главной страницы."""

    @classmethod
    def setUpTestData(cls):
        """Создает дополнительные тестовые данные для главной страницы."""
        super().setUpTestData()

        all_notes = [
            Note(
                title=f'Заметка {index}',
                text='Просто текст.',
                slug=f'note-{index}',
                author=cls.author,
            )
            for index in range(10)
        ]
        Note.objects.bulk_create(all_notes)

    def test_notes_order(self):
        """Проверяет, что главная страница возвращает статус 200."""
        response = self.client.get(self.HOME_URL)
        self.assertEqual(response.status_code, 200)


class TestDetailPage(BaseTest):
    """Тесты для страницы деталей заметки."""

    def test_note_detail(self):
        """Проверяет, что страница деталей заметки возвращает статус 200."""
        response = self.client.get(self.detail_url)
        self.client.force_login(self.author)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('note', response.context)


class TestNotePermissions(BaseTest):
    """Тесты для проверки прав доступа к заметкам."""

    @classmethod
    def setUpTestData(cls):
        """Создает тестовые данные для проверки прав доступа."""
        super().setUpTestData()
        cls.another_user = User.objects.create(username='Другой пользователь')

    def test_author_can_edit_and_delete(self):
        """Проверяет, что автор может редактировать и удалять свою заметку."""
        self.client.force_login(self.author)
        response_edit = self.client.get(self.edit_url)
        response_delete = self.client.get(self.delete_url)
        self.assertEqual(response_edit.status_code, 200)
        self.assertEqual(response_delete.status_code, 200)

    def test_another_user_cannot_edit_or_delete(self):
        """
        Проверяет, что другой пользователь не может редактировать или
        удалять чужую заметку.
        """
        self.client.force_login(self.another_user)
        response_edit = self.client.get(self.edit_url)
        response_delete = self.client.get(self.delete_url)
        self.assertEqual(response_edit.status_code, 404)
        self.assertEqual(response_delete.status_code, 404)


class TestPublicPages(BaseTest):
    """Тесты для публичных страниц (регистрация, вход, выход)."""

    def test_registration_page_accessible(self):
        """Проверяет доступность страницы регистрации."""
        response = self.client.get(reverse('users:signup'))
        self.assertEqual(response.status_code, 200)

    def test_login_page_accessible(self):
        """Проверяет доступность страницы входа."""
        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)

    def test_logout_page_accessible(self):
        """Проверяет доступность страницы выхода."""
        response = self.client.get(reverse('users:logout'))
        self.assertEqual(response.status_code, 200)


class TestAnonymousRedirect(BaseTest):
    """Тесты для проверки редиректов анонимных пользователей."""

    def test_anonymous_redirected_to_login_on_list_page(self):
        """
        Проверяет редирект анонимного пользователя на страницу входа
        при попытке доступа к списку заметок.
        """
        response = self.client.get(self.LIST_URL)
        self.assertRedirects(
            response, f"{reverse('users:login')}?next={self.LIST_URL}"
        )

    def test_anonymous_redirected_to_login_on_add_page(self):
        """
        Проверяет редирект анонимного пользователя на страницу входа
        при попытке доступа к странице добавления заметки.
        """
        response = self.client.get(self.ADD_URL)
        self.assertRedirects(
            response, f"{reverse('users:login')}?next={self.ADD_URL}"
        )

    def test_anonymous_redirected_to_login_on_detail_page(self):
        """
        Проверяет редирект анонимного пользователя на страницу входа
        при попытке доступа к странице деталей заметки.
        """
        response = self.client.get(self.detail_url)
        self.assertRedirects(
            response, f"{reverse('users:login')}?next={self.detail_url}"
        )

    def test_anonymous_redirected_to_login_on_edit_page(self):
        """
        Проверяет редирект анонимного пользователя на страницу входа
        при попытке доступа к странице редактирования заметки.
        """
        response = self.client.get(self.edit_url)
        self.assertRedirects(
            response, f"{reverse('users:login')}?next={self.edit_url}"
        )

    def test_anonymous_redirected_to_login_on_delete_page(self):
        """
        Проверяет редирект анонимного пользователя на страницу входа
        при попытке доступа к странице удаления заметки.
        """
        response = self.client.get(self.delete_url)
        self.assertRedirects(
            response, f"{reverse('users:login')}?next={self.delete_url}"
        )


class TestAuthenticatedAccess(BaseTest):
    """Тесты для проверки доступа авторизованных пользователей."""

    def test_authenticated_user_can_access_list_page(self):
        """
        Проверяет, что авторизованный пользователь может получить доступ
        к странице списка заметок.
        """
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        self.assertEqual(response.status_code, 200)

    def test_authenticated_user_can_access_add_page(self):
        """
        Проверяет, что авторизованный пользователь может получить доступ
        к странице добавления заметки.
        """
        self.client.force_login(self.author)
        response = self.client.get(self.ADD_URL)
        self.assertEqual(response.status_code, 200)

    def test_authenticated_user_can_access_success_page(self):
        """
        Проверяет, что авторизованный пользователь может получить доступ
        к странице успешного завершения.
        """
        self.client.force_login(self.author)
        response = self.client.get(self.SUCCESS_URL)
        self.assertEqual(response.status_code, 200)
