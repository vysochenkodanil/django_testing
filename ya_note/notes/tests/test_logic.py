from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import Client, TestCase
from django.urls import reverse
from notes.models import Note

User = get_user_model()


class NoteCreationTest(TestCase):
    """Тесты для создания заметки."""

    @classmethod
    def setUpTestData(cls):
        """Создает тестовые данные для создания заметки."""
        cls.user = User.objects.create(username='testuser')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.url = reverse('notes:add')
        cls.form_data = {
            'title': 'Новая заметка',
            'text': 'Текст новой заметки',
        }

    def test_anonymous_user_cant_create_note(self):
        """Проверяет, что анонимный пользователь не может создать заметку."""
        initial_count = Note.objects.count()
        response = self.client.post(self.url, data=self.form_data)
        login_url = reverse('users:login')
        redirect_url = f'{login_url}?next={self.url}'
        self.assertRedirects(response, redirect_url)
        self.assertEqual(Note.objects.count(), initial_count)

    def test_user_can_create_note(self):
        """Проверяет, что авторизованный пользователь может создать заметку."""
        initial_count = Note.objects.count()
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), initial_count + 1)
        note = Note.objects.latest('id')
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.author, self.user)

    def test_slug_uniqueness(self):
        """Проверяет уникальность slug."""
        Note.objects.create(title='Тест', text='Текст', author=self.user)
        with self.assertRaises(IntegrityError):
            Note.objects.create(
                title='Тест', text='Другой текст', author=self.user
            )


class NoteEditDeleteTest(TestCase):
    """Тесты для редактирования и удаления заметок."""

    @classmethod
    def setUpTestData(cls):
        """Создает тестовые данные для редактирования и удаления заметок."""
        cls.author = User.objects.create(username='author')
        cls.reader = User.objects.create(username='reader')

        cls.initial_title = 'Тестовая заметка'
        cls.initial_text = 'Текст тестовой заметки.'
        cls.updated_title = 'Обновленная заметка'
        cls.updated_text = 'Обновленный текст заметки.'

        cls.note = Note.objects.create(
            title=cls.initial_title,
            text=cls.initial_text,
            author=cls.author
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {
            'title': cls.updated_title,
            'text': cls.updated_text,
        }

    def test_author_can_edit_note(self):
        """Проверяет, что автор может редактировать свою заметку."""
        self.client.force_login(self.author)
        response = self.client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.updated_title)
        self.assertEqual(self.note.text, self.updated_text)

    def test_reader_cant_edit_note(self):
        """
        Проверяет, что другой пользователь
        не может редактировать чужую заметку.
        """
        self.client.force_login(self.reader)
        response = self.client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND.value)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.initial_title)
        self.assertEqual(self.note.text, self.initial_text)

    def test_author_can_delete_note(self):
        """Проверяет, что автор может удалить свою заметку."""
        self.client.force_login(self.author)
        initial_count = Note.objects.count()
        response = self.client.post(self.delete_url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), initial_count - 1)

    def test_reader_cant_delete_note(self):
        """
        Проверяет, что другой пользователь
        не может удалить чужую заметку.
        """
        self.client.force_login(self.reader)
        initial_count = Note.objects.count()
        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND.value)
        self.assertEqual(Note.objects.count(), initial_count)
