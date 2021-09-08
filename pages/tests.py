from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from tweets.models import Tweet, Comment, UserFollowing

class TestTweetsAndComments(TestCase):
    
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='usertest',
            email='usertest@email.com',
            password='testpass123'
        )
        
        self.secondUser = get_user_model().objects.create_user(
            username='usertest2',
            email='usertest2@email.com',
            password='testpass123'
        )
        
        self.tweet = Tweet.objects.create(
            content='First tweet',
            author=self.user
        )
        
        self.secondTweet = Tweet.objects.create(
            content='Second tweet',
            author=self.secondUser
        )
        
        self.comment = Comment.objects.create(
            tweet=self.tweet,
            comment='Test comment on a tweet',
            author=self.user
        )
        
    def test_tweet_list_homepage_for_logged_in_user(self):
        self.client.login(username='usertest', password='testpass123')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'First tweet')
        self.assertTemplateUsed(response, 'pages/home.html')
        
    def test_tweet_list_homepage_for_logged_out_user(self):
        self.client.logout()
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome to Twitter Clone!')
        self.assertTemplateUsed(response, 'pages/home.html')
        
    def test_tweet_detail_view_for_logged_in_user(self):
        self.client.login(username='usertest', password='testpass123')
        response = self.client.get(self.tweet.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'First tweet')
        self.assertContains(response, 'Test comment on a tweet')
        self.assertContains(response, 'usertest')
        self.assertTemplateUsed(response, 'pages/tweet_detail.html')
        
    def test_tweet_detail_view_for_logged_out_user(self):
        self.client.logout()
        response = self.client.get(self.tweet.get_absolute_url())
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '%s?next=%s' % (reverse('account_login'), self.tweet.get_absolute_url()))
        response = self.client.get('%s?next=%s' % (reverse('account_login'), self.tweet.get_absolute_url()))
        self.assertContains(response, 'Log In')
        
    def test_tweet_list_user_detail_for_logged_in_user(self):
        self.client.login(username='usertest', password='testpass123')
        response = self.client.get(reverse('user_detail', args=[str(self.secondUser.pk)]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Usertest2')
        self.assertContains(response, 'Second tweet')
        self.assertTemplateUsed(response, 'pages/user_detail.html')
        
    def test_tweet_list_user_detail_for_logged_out_user(self):
        self.client.logout()
        response = self.client.get(reverse('user_detail', args=[str(self.secondUser.pk)]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '%s?next=%s' % (reverse('account_login'), reverse('user_detail', args=[str(self.secondUser.pk)])))
        response = self.client.get('%s?next=%s' % (reverse('account_login'), reverse('user_detail', args=[str(self.secondUser.pk)])))
        self.assertContains(response, 'Log In')
        
    def test_tweet_list_my_profile_for_logged_in_user(self):
        self.client.login(username='usertest', password='testpass123')
        response = self.client.get(reverse('myProfile_detail', args=[str(self.user.pk)]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Usertest')
        self.assertContains(response, 'First tweet')
        self.assertTemplateUsed(response, 'pages/myProfile_detail.html')
        
class TestUserFollowing(TestCase):
    
    def setUp(self):
        self.user1 = get_user_model().objects.create_user(
            username='usertest1',
            email='usertest1@email.com',
            password='testpass123'
        )
        
        self.user2 = get_user_model().objects.create_user(
            username='usertest2',
            email='usertest2@email.com',
            password='testpass123'
        )
        
        self.user1FollowingUser2 = UserFollowing.objects.create(
            user_id=self.user1,
            following_user_id=self.user2
        )
        
        self.tweet = Tweet.objects.create(
            content='First tweet',
            author=self.user2
        )
        
    def test_user_following_tweet_visibility_on_tweet_list(self):
        self.client.login(username='usertest1', password='testpass123')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'First tweet')
        self.assertContains(response, 'usertest2')
        self.assertTemplateUsed(response, 'pages/home.html')
        
    def test_user_unfollowing_button_visibility_user_detail(self):
        self.client.login(username='usertest1', password='testpass123')
        response = self.client.get(reverse('user_detail', args=[str(self.user2.pk)]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Usertest2')
        self.assertContains(response, 'Unfollow')
        self.assertTemplateUsed(response, 'pages/user_detail.html')
        
    def test_user_following_button_visibility_user_detail(self):
        self.client.login(username='usertest2', password='testpass123')
        response = self.client.get(reverse('user_detail', args=[str(self.user1.pk)]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Usertest1')
        self.assertContains(response, 'Follow')
        self.assertTemplateUsed(response, 'pages/user_detail.html')