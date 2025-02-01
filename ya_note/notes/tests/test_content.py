from http import HTTPStatus

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

    def test_home_page_status_code(self):
        """Проверяет, что главная страница возвращает статус 200."""
        response = self.client.get(self.HOME_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_home_page_template(self):
        """
        Проверяет,
        что используется правильный шаблон для главной страницы.
        """
        response = self.client.get(self.HOME_URL)
        self.assertTemplateUsed(response, 'notes/home.html')


class TestDetailPage(BaseTest):
    """Тесты для страницы деталей заметки."""

    def test_note_detail(self):
        """
        Проверяет доступ к странице деталей заметки
        и корректность данных.
        """
        self.client.force_login(self.author)
        self.assertTrue(Note.objects.filter(slug=self.note.slug).exists())
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, HTTPStatus.OK.value)
        self.assertIn('note', response.context)
        note = response.context['note']
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertTemplateUsed(response, 'notes/detail.html')


class TestNotesListPage(BaseTest):
    """Тесты для страницы списка заметок."""

    def test_note_in_object_list(self):
        """Проверяет, что заметка автора присутствует в списке."""
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK.value)
        self.assertIn('object_list', response.context)
        self.assertIn(self.note, response.context['object_list'])

    def test_note_not_in_another_users_list(self):
        """Проверяет, что чужая заметка не отображается в списке."""
        another_user = User.objects.create(username='Другой пользователь')
        another_note = Note.objects.create(
            title='Чужая заметка',
            text='Текст чужой заметки',
            slug='another-note',
            author=another_user
        )
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        self.assertNotIn(another_note, response.context['object_list'])


class TestAccess(BaseTest):
    """Тесты для проверки доступа к страницам."""

    def test_anonymous_client_redirect(self):
        """Проверяет редирект анонимного пользователя на страницу входа."""
        urls = (
            self.ADD_URL,
            self.detail_url,
            self.edit_url,
            self.delete_url,
            self.LIST_URL,
            self.SUCCESS_URL,
        )
        login_url = reverse('users:login')
        for url in urls:
            with self.subTest(url=url):
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_authorized_client_access(self):
        """Проверяет доступ авторизованного пользователя к страницам."""
        self.client.force_login(self.author)
        urls = (
            self.HOME_URL,
            self.ADD_URL,
            self.detail_url,
            self.edit_url,
            self.delete_url,
            self.LIST_URL,
            self.SUCCESS_URL,
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK.value)


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
        self.assertEqual(response_edit.status_code, HTTPStatus.OK.value)
        self.assertEqual(response_delete.status_code, HTTPStatus.OK.value)

    def test_another_user_cannot_edit_or_delete(self):
        """
        Проверяет, что другой пользователь не может редактировать или
        удалять чужую заметку.
        """
        self.client.force_login(self.another_user)
        response_edit = self.client.get(self.edit_url)
        response_delete = self.client.get(self.delete_url)
        self.assertEqual(response_edit.status_code, HTTPStatus.NOT_FOUND.value)
        self.assertEqual(
            response_delete.status_code,
            HTTPStatus.NOT_FOUND.value
        )

    def test_add_page_contains_form(self):
        """Проверяет, что страница добавления заметки содержит форму."""
        self.client.force_login(self.author)
        response = self.client.get(self.ADD_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK.value)
        self.assertIn('form', response.context)

    def test_edit_page_contains_form(self):
        """Проверяет, что страница редактирования заметки содержит форму."""
        self.client.force_login(self.author)
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, HTTPStatus.OK.value)
        self.assertIn('form', response.context)
