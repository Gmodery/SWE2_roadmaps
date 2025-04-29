from django.test import TestCase
from .models import AppUser
from .forms import SignUpForm
from django.urls import reverse

class AppUserTestCase(TestCase):
    """Test for creating, querying, and deleting users from database"""

    def setUp(self):
        # Set up initial data for the test database
        AppUser.objects.create(username="Test 1", first_name="Test 1", last_name="Test 1",
                               email="Test1@test.com", password="Test1Test1", role="student")
        AppUser.objects.create(username="Test 2", first_name="Test 2", last_name="Test 2",
                               email="Test2@test.com", password="Test2Test2", role="instructor")

    def test_model_query(self):
        """Test retrieving data from the database"""
        obj = AppUser.objects.get(username="Test 1")
        self.assertEqual(obj.last_name, "Test 1")

        obj = AppUser.objects.get(username="Test 2")
        self.assertEqual(obj.last_name, "Test 2")

    def test_delete_entry(self):
        """Test deleting a database entry"""
        AppUser.objects.get(username="Test 1").delete()
        AppUser.objects.get(username="Test 2").delete()
        self.assertEqual(AppUser.objects.count(), 0)


class FormTestCase(TestCase):
    """Test for the signup form and ensuring that only valid forms are considered"""

    def test_valid_form(self):
        """Test valid form submission"""
        form_data = {'username': 'Test', 'first_name': 'Test', 'last_name': 'Test', 
                     'email': 'test@test.com', 'password1': 'Test1Test1', 
                     'password2': 'Test1Test1', 'role': 'student',}
        form = SignUpForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_incomplete_form(self):
        """Test form with missing fields"""
        form_data = {'username': 'Test', 'first_name': 'Test', 'last_name': '', 
                     'email': 'test@test.com', 'password1': 'Test1Test1', 
                     'password2': 'Test1Test1', 'role': 'student',}
        form = SignUpForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_invalid_form(self):
        """Test form with non-matching passwords"""
        form_data = {'username': 'Test', 'first_name': 'Test', 'last_name': 'Test', 
                     'email': 'test@test.com', 'password1': 'Test1Test1', 
                     'password2': 'Test2', 'role': 'student',}
        form = SignUpForm(data=form_data)
        self.assertFalse(form.is_valid())


class NavigationTestCase(TestCase):
    """Test navigation between pages"""

    def test_home_page_access(self):
        """Test that the home page returns a 200 response"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_login_page_access(self):
        """Test that the login page returns a 200 response"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_signup_page_access(self):
        """Test that the signup page returns a 200 response"""
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)

    def test_redirect_if_not_logged_in(self):
        """Test redirection for pages requiring login"""
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, '/login/?next=/pages/dashboard')