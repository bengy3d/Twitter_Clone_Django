from django.urls import path

from .views import (
    LandingPageView,
    LoginTemplateView,
    ExploreListView,
    MyProfileDetailView,
    SearchResultsListView, 
    UserDetailView,
    TweetDetailView,
    TweetListView,
    TweetCreateView,
    TweetDeleteView,
    MyProfileDetailView,
    UserUnfollowView,
    like_tweet,
    unlike_tweet,
    like_comment,
    unlike_comment
)

urlpatterns = [
    path('', LandingPageView.as_view(), name='landing'),
    path('login/', LoginTemplateView.as_view(), name='login'),
    path('home/', TweetListView.as_view(), name='home'),
    path('explore/', ExploreListView.as_view(), name='explore'),
    path('search/', SearchResultsListView.as_view(), name='search_results'),
    path('users/<uuid:pk>', UserDetailView.as_view(), name='user_detail'),
    path('users/<uuid:pk>/unfollow/', UserUnfollowView.as_view(), name='user_unfollow'),
    path('my_profile/', MyProfileDetailView.as_view(), name='my_profile_detail'),
    path('tweets/create/', TweetCreateView.as_view(), name='tweet_create'),
    path('tweets/<uuid:pk>/', TweetDetailView.as_view(), name='tweet_detail'),
    path('tweets/<uuid:pk>/delete/', TweetDeleteView.as_view(), name="tweet_delete"),
    path('like_tweet/<uuid:pk>/', like_tweet, name='like_tweet'),
    path('unlike_tweet/<uuid:pk>/', unlike_tweet, name='unlike_tweet'),
    path('like_comment/<uuid:pk>/', like_comment, name='like_comment'),
    path('unlike_comment/<uuid:pk>/', unlike_comment, name='unlike_comment'),
]