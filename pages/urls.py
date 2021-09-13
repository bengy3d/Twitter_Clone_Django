from django.urls import path

from .views import (
    MyProfileDetailView,
    SearchResultsListView, 
    UserDetailView,
    TweetDetailView,
    TweetListView,
    MyProfileDetailView,
    UserUnfollowView,
    like_tweet,
    unlike_tweet
)

urlpatterns = [
    path('', TweetListView.as_view(), name='home'),
    path('search/', SearchResultsListView.as_view(), name='search_results'),
    path('users/<int:pk>', UserDetailView.as_view(), name='user_detail'),
    path('users/<int:pk>/unfollow/', UserUnfollowView.as_view(), name='user_unfollow'),
    path('my_profile/<int:pk>', MyProfileDetailView.as_view(), name='my_profile_detail'),
    path('tweets/<uuid:pk>', TweetDetailView.as_view(), name='tweet_detail'),
    path('like/<uuid:pk>', like_tweet, name='like_tweet'),
    path('unlike/<uuid:pk>', unlike_tweet, name='unlike_tweet')
]