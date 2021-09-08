from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, FormView, DeleteView
from django.views import View
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.urls import reverse, reverse_lazy

from tweets.models import Tweet, UserFollowing
from .forms import CommentForm, TweetForm, FollowForm

userModel = get_user_model()

# Homepage View
class TweetListDisplay(ListView):
    model = Tweet
    context_object_name = 'tweet'
    template_name = 'pages/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = TweetForm()
        return context
    
class TweetFormView(FormView):
    model = Tweet
    form_class = TweetForm
    template_name = 'pages/home.html'
    
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def form_valid(self, form):
        tweet = form.save(commit=False)
        tweet.author = self.request.user
        tweet.save()
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('myProfile_detail', kwargs={'pk': self.request.user.pk})
    
class TweetListView(View):

    def get(self, request, *args, **kwargs):
        view = TweetListDisplay.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = TweetFormView.as_view()
        return view(request, *args, **kwargs)
    
# Tweet detail Views
class TweetDisplay(DetailView):
    model = Tweet
    template_name = 'pages/tweet_detail.html'
    context_object_name = 'tweet'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        return context
    
class TweetComment(SingleObjectMixin, FormView):
    model = Tweet
    form_class = CommentForm
    template_name = 'pages/tweet_detail.html'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(TweetComment, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.tweet = self.object
        comment.author = self.request.user
        comment.save()
        return super().form_valid(form)

    def get_success_url(self):
        post = self.get_object()
        return reverse('tweet_detail', kwargs={'pk': post.pk}) + '#comments'
    
class TweetDetailView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        view = TweetDisplay.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = TweetComment.as_view()
        return view(request, *args, **kwargs)

# Search results list View
class SearchResultsListView(LoginRequiredMixin, ListView):
    model = userModel
    template_name = 'pages/search_results.html'
    login_ulr = 'account_login'
    
    def get_queryset(self):
        query = self.request.GET.get('q')
        if not query:
            return 
        return userModel.objects.filter(
            Q(username__icontains=query)
        )

# My profile Detail Views
class MyProfileDisplay(DetailView):
    model = userModel
    context_object_name = 'person'
    template_name = 'pages/myProfile_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = TweetForm()
        return context

class MyProfileTweetFormView(FormView):
    model = Tweet
    form_class = TweetForm
    template_name = 'pages/myProfile_detail.html'
    
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def form_valid(self, form):
        my_profile = userModel.objects.get(username=self.request.user)
        tweet = form.save(commit=False)
        tweet.author = self.request.user
        tweet.save()
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('myProfile_detail', kwargs={'pk': self.request.user.pk}) + '#new_post'
       
class MyProfileDetailView(LoginRequiredMixin, DetailView):
    
    def get(self, request, *args, **kwargs):
        view = MyProfileDisplay.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = MyProfileTweetFormView.as_view()
        return view(request, *args, **kwargs)
    
# User profile Detail views and UserFollowingform
class UserDisplay(DetailView):
    model = userModel
    context_object_name = 'person'
    template_name = 'pages/user_detail.html'
    
    def get_object(self, **kwargs):
        primaryKey = self.kwargs.get('pk')
        view_user = userModel.objects.get(pk=primaryKey)
        return view_user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = FollowForm()
        view_user = self.get_object()
        my_profile = userModel.objects.get(username=self.request.user)
        follow = True
        for followed in my_profile.following.all():
            if followed.following_user_id == view_user:
                follow = False
        print(follow)
        context['follow'] = follow
        return context

class UserFollowFormView(SingleObjectMixin, FormView):
    model = userModel
    form_class = FollowForm
    template_name = 'pages/user_detail.html'
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super(UserFollowFormView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def form_valid(self, form):
        follow = form.save(commit=False)
        follow.user_id = self.request.user
        follow.following_user_id = self.object
        follow.save()
        return super().form_valid(form)
    
    def get_success_url(self):
        post = self.get_object()
        return reverse('user_detail', kwargs={'pk': post.pk})
       
class UserDetailView(LoginRequiredMixin, DetailView):
    
    def get(self, request, *args, **kwargs):
        view = UserDisplay.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = UserFollowFormView.as_view()
        return view(request, *args, **kwargs)
    
class UserUnfollowView(LoginRequiredMixin, FormView):
    model = UserFollowing
    form_class = FollowForm
    template_name = 'pages/user_unfollow.html'
    
    def get_object(self, **kwargs):
        primaryKey = self.kwargs.get('pk')
        view_user = userModel.objects.get(pk=primaryKey)
        return view_user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        view_user = self.get_object()
        context['person'] = view_user
        return context
    
    def form_valid(self, form):
        view_user = self.get_object()
        my_profile = userModel.objects.get(username=self.request.user)
        for follow in my_profile.following.all():
            if view_user == follow.following_user_id:
                follow.delete()
        return super().form_valid(form)
    
    def get_success_url(self):
        view_user = self.get_object()
        return reverse('user_detail', kwargs={'pk': view_user.pk})