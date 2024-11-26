from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
from notes.models import Note
from django.contrib.auth import get_user_model


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Kristina')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='note_1',
            author=cls.author
        )

    def test_pages_availability(self):
        """
        Проверяем, что главная страница, страницы регистрации пользователей, 
        входа в учётную запись и выхода из неё 
        доступны анонимным пользователям.
        """
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_login_user(self):
        """
        Проверяем, что страница отдельной заметки, страницы
        удаления и редактирования заметки доступны автору заметки.
        """
        urls = (
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),

        )
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            # Логиним пользователя в клиенте:
            self.client.force_login(user)
            # Для каждой пары "пользователь - ожидаемый ответ"
            # перебираем имена тестируемых страниц:
            for name, args in urls:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_page_list_availability(self):
        """
        Проверяем, что страница с заметками и добавлением
        доступна авторизированному пользователю
        """
        users = [
            self.author,
            self.reader,
        ]
        urls = (
            ('notes:list', None),
            ('notes:add', None),
        )
        for user in users:
            self.client.force_login(user)
            for name, args in urls:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)
    
    def test_redirect_for_anonymous_client(self):
        # Сохраняем адрес страницы логина:
        login_url = reverse('users:login')
        # В цикле перебираем имена страниц, с которых ожидаем редирект:
        for name in ('notes:edit', 'notes:delete'):
            with self.subTest(name=name):
                # Получаем адрес страницы редактирования или удаления комментария:
                url = reverse(name, args=(self.note.slug,))
                # Получаем ожидаемый адрес страницы логина, 
                # на который будет перенаправлен пользователь.
                # Учитываем, что в адресе будет параметр next, в котором передаётся
                # адрес страницы, с которой пользователь был переадресован.
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                # Проверяем, что редирект приведёт именно на указанную ссылку.
                self.assertRedirects(response, redirect_url) 
        
