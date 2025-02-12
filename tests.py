from django.test import Client, TestCase
from webShop.models import User
from webShop.models import ContactMessage
import unittest


class contactTest(unittest.TestCase):

    def test_contact(self):
        #self.user = User.objects.create_user(username='testuser', password='12345')
        #login = self.client.login(username='testuser', password='12345')
        c = Client()
        resp = c.get('/contacted/')
        self.assertEqual(resp.status_code, 200)



class warenkorb(unittest.TestCase):

    def test_warenkorb(self):

        c = Client()
        resp = c.get('/warenkorb/')
        self.assertEqual(resp.status_code, 200)


class preferences(unittest.TestCase):

    def test_preference(self):
        c = Client()
        resp = c.get('/preferences/')
        self.assertEqual(resp.status_code, 200)

class payment(unittest.TestCase):

    def test_payment(self):
        c = Client()
        resp = c.get('/login/')
        self.assertEqual(resp.status_code, 200)

class about(unittest.TestCase):

    def test_about(self):
        c = Client()
        resp = c.get('/about/')
        self.assertEqual(resp.status_code, 200)



