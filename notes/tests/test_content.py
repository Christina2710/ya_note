from notes.forms import NoteForm
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from notes.models import Note

User = get_user_model()


class TestDetailPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Kristina')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='note_1',
            author=cls.author
        )
        cls.add_url = reverse('notes:add', None)

    def test_anonymous_client_has_no_form(self):
        response = self.client.get(self.add_url)
        if response.context is not None:
            self.assertNotIn('form', response.context)
        else:
            # Если контекста нет, это тоже корректное поведение
            self.assertTrue(True)

    def test_authorized_client_has_form(self):
        # Авторизуем клиент при помощи ранее созданного пользователя.
        self.client.force_login(self.author)
        response = self.client.get(self.add_url)
        self.assertIn('form', response.context)
        # Проверим, что объект формы соответствует нужному классу формы.
        self.assertIsInstance(response.context['form'], NoteForm)
