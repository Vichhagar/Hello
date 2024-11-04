from django.test import TestCase, Client
from django.urls import reverse
from hello_public.models import *
from .models import ActivityLocation, Activity
from .forms import ActivityForm

class TestCreatePost(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
    
    def test_create_post(self):
        # simulate a POST request to create a new post
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('hello_public:create_post'), data={'postText': 'Test post'}, follow=True)

        # ensure the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # ensure the new post was created and associated with the user
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.first()
        self.assertEqual(post.userId, self.user)
        self.assertEqual(post.postText, 'Test post')

class TestDeletePost(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.post = Post.objects.create(userId=self.user, postText='Test post')

    def test_delete_post(self):
        # log in the user
        self.client.login(username='testuser', password='testpass')

        # simulate a POST request to delete the post
        response = self.client.post(reverse('hello_public:delete_post', args=[self.post.id]), follow=True)

        # ensure the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # ensure the post is marked as deleted
        post = Post.objects.get(id=self.post.id)
        self.assertEqual(post.postStatus, 'in_bin')

        # ensure the user is redirected to the home page after deleting the post
        self.assertRedirects(response, reverse('hello_public:user_dashboard'))

class CreateActivityViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.url = reverse('hello_public:activity_create')
        self.activity_location = ActivityLocation.objects.create(location_name='New York')

    def test_create_activity_view_with_valid_data(self):
        form_data = {
            'activityTitle': 'Test Activity',
            'activityLocation': 'New York',
            'activityDiscription': 'Test activity description',
            'activityOpenDate': '2023-05-04T04:00',
            'activityCloseDate': '2023-05-26T00:00',
            'activityDate': '2023-05-27T00:00',
        }
        response = self.client.post(self.url, data=form_data)
        self.assertEqual(response.status_code, 302) # Check if it redirects to the activity detail page
        activity = Activity.objects.get(activityTitle='Test Activity')
        self.assertEqual(activity.activityOrganizer, self.user) # Check if the activity organizer is the logged-in user

    def test_create_activity_view_with_invalid_data(self):
        form_data = {
            'activityTitle': 'Test Activity',
            'activityLocation': 'New York',
            'activityDiscription': 'Test activity description',
            'activityOpenDate': '2023-05-04T04:00',
            'activityCloseDate': '2023-05-26T00:00',
            'activityDate': '2023-05-24T00:00', # Invalid activity date (before close date)
        }

        response = self.client.post(self.url, data=form_data)
        self.assertEqual(response.status_code, 200) # Check if it stays on the create activity page
        self.assertContains(response, 'Activity date must be after close date.') # Check if the error message is displayed
        self.assertFalse(Activity.objects.filter(activityTitle='Test Activity').exists()) # Check if the activity is not saved to the database

class DeleteActivityViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.activity = Activity.objects.create(
            activityTitle='Test Activity',
            activityLocation='Test Location',
            activityOrganizer=self.user,
            activityOpenDate='2023-05-04T04:00',
            activityCloseDate='2023-05-26T00:00',
            activityDiscription='This is a test activity.',
            activityDate = '2023-05-27T00:00'
        )
        self.url = reverse('hello_public:delete_activity', kwargs={'pk': self.activity.pk})

    def test_delete_activity_view_with_valid_user(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('hello_public:user_dashboard'))

        activity_exists = Activity.objects.filter(pk=self.activity.pk).exists()
        self.assertFalse(activity_exists)

    def test_delete_activity_view_with_invalid_user(self):
        User.objects.create_user(username='otheruser', password='otherpass')
        self.client.login(username='otheruser', password='otherpass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 404)
