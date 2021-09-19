from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView, DetailView, FormView, DeleteView, TemplateView
)
from django.views import View
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth import get_user_model, login
from django.db.models import Q
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect, Http404
from django.views.generic.edit import CreateView

from notifications.signals import notify

from tweets.models import Tweet, UserFollowing, Comment
from .forms import CommentForm, TweetForm, FollowForm

userModel = get_user_model()


# Landing page view
class LandingPageView(TemplateView):
    template_name = 'pages/landing_page.html'
    
    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('home'))
        return super().get(request, *args, **kwargs)
    
class LoginTemplateView(LandingPageView):
    template_name = 'pages/login.html'
    
# Homepage View
# GET
class TweetListDisplay(ListView):
    model = Tweet
    context_object_name = 'tweet'
    template_name = 'pages/home.html'
    paginate_by = 20
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_profile = userModel.objects.get(username=self.request.user)
        is_liked = {}
        for tweet in self.object_list.all():
            if tweet in my_profile.tweet_likes.all():
                is_liked[tweet.pk] = True
            else:
                is_liked[tweet.pk] = False
        context['is_liked'] = is_liked
        context['form'] = TweetForm()
        return context
    
    def get_queryset(self):
        followed_users = self.request.user.following.all()
        followed_users = list(followed_users.values_list('following_user_id', flat=True))
        followed_users.append(self.request.user.pk)
        return Tweet.objects.filter(
            Q(author__pk__in=followed_users)
        )
# POST    
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
        return reverse('home') + '#new_post'
    
class TweetListView(LoginRequiredMixin, View):

    login_url = 'login'

    def get(self, request, *args, **kwargs):
        view = TweetListDisplay.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = TweetFormView.as_view()
        return view(request, *args, **kwargs)
    
class ExploreDisplay(TweetListDisplay):
    template_name = 'pages/explore.html'
    
    def get_queryset(self):
        return Tweet.objects.all()

class ExploreFormView(TweetFormView):
    template_name = 'pages/explore.html'
    
    def get_success_url(self):
        return reverse('explore')
    
class ExploreListView(LoginRequiredMixin, View):
    
    login_url = 'login'
    
    def get(self, request, *args, **kwargs):
        view = ExploreDisplay.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = ExploreFormView.as_view()
        return view(request, *args, **kwargs)

# Tweet detail Views
# GET
class TweetDisplay(DetailView):
    model = Tweet
    template_name = 'pages/tweet_detail.html'
    context_object_name = 'tweet'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_profile = userModel.objects.get(username=self.request.user)
        liked = False
        if self.object in my_profile.tweet_likes.all():
            liked = True
        context['liked'] = liked
        is_liked = {}
        for comment in self.object.comments.all():
            if comment in my_profile.comment_likes.all():
                is_liked[comment.pk] = True
            else:
                is_liked[comment.pk] = False
        context['is_liked'] = is_liked
        context['form'] = CommentForm()
        return context
# POST    
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
        if comment.author != self.object.author:
            notify.send(sender=comment.author, recipient=comment.tweet.author, 
                        action_object=comment.tweet, target=comment, verb='Comment',
                        description='commented on your tweet')
        comment.save()
        return super().form_valid(form)

    def get_success_url(self):
        post = self.get_object()
        return reverse('tweet_detail', kwargs={'pk': post.pk}) + '#comments'
    
class TweetDetailView(LoginRequiredMixin, View):
    
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        view = TweetDisplay.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = TweetComment.as_view()
        return view(request, *args, **kwargs)
    
class TweetCreateView(LoginRequiredMixin, CreateView):
    model = Tweet
    template_name = 'pages/tweet_create.html'
    form_class = TweetForm
    login_url = 'login'
    
    def form_valid(self, form):
        tweet = form.save(commit=False)
        tweet.author = self.request.user
        tweet.save()
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('home')

class TweetDeleteView(LoginRequiredMixin, DeleteView):
    model = Tweet
    template_name = 'pages/tweet_delete.html'
    success_url = reverse_lazy('my_profile_detail')
    login_url = 'login'
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.author == request.user:
            return super(TweetDeleteView, self).delete(request, *args, 
                                                       **kwargs)
        else:
            raise(Http404('permission denied'))
    

# Search results list View
class SearchResultsListView(LoginRequiredMixin, ListView):
    model = userModel
    template_name = 'pages/search_results.html'
    login_url = 'login'
    paginate_by = 10
    
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
    template_name = 'pages/my_profile_detail.html'
    
    def get_object(self):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        my_profile = userModel.objects.get(username=self.request.user)
        is_liked = {}
        for tweet in my_profile.tweets.all():
            if tweet in my_profile.tweet_likes.all():
                is_liked[tweet.pk] = True
            else:
                is_liked[tweet.pk] = False
        context['is_liked'] = is_liked
        context['form'] = TweetForm()
        return context

class MyProfileTweetFormView(FormView):
    model = Tweet
    form_class = TweetForm
    template_name = 'pages/my_profile_detail.html'
    
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def form_valid(self, form):
        tweet = form.save(commit=False)
        tweet.author = self.request.user
        tweet.save()
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('my_profile_detail') + '#new_post'
       
class MyProfileDetailView(LoginRequiredMixin, DetailView):
    login_url = 'login'
    
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
        is_liked = {}
        for tweet in view_user.tweets.all():
            if tweet in my_profile.tweet_likes.all():
                is_liked[tweet.pk] = True
            else:
                is_liked[tweet.pk] = False
        context['is_liked'] = is_liked
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
        notify.send(sender=follow.user_id, recipient=follow.following_user_id, 
                    action_object=follow.user_id, verb='user-follow',
                    description='started following you')
        follow.save()
        return super().form_valid(form)
    
    def get_success_url(self):
        post = self.get_object()
        return reverse('user_detail', kwargs={'pk': post.pk})
       
class UserDetailView(LoginRequiredMixin, DetailView):
    
    login_url = 'login'
    
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
    login_url = 'login'
    
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
    
def like_tweet(request, pk):
    tweet = get_object_or_404(Tweet, id=request.POST.get('tweet_id'))
    next = request.POST.get('next', '/')
    if tweet.author != request.user:
        notify.send(sender=request.user, recipient=tweet.author, 
                    action_object=tweet, verb='tweet-like',
                    description='liked your tweet')
    tweet.likes.add(request.user)
    return HttpResponseRedirect(next + f'#{tweet.pk}')

def unlike_tweet(request, pk):
    tweet = get_object_or_404(Tweet, id=request.POST.get('tweet_id'))
    next = request.POST.get('next', '/')
    tweet.likes.remove(request.user)
    return HttpResponseRedirect(next + f'#{tweet.pk}') 

def like_comment(request, pk):
    comment = get_object_or_404(Comment, id=request.POST.get('comment_id'))
    next = request.POST.get('next', '/')
    if comment.author != request.user:
        notify.send(sender=request.user, recipient=comment.author, 
                    action_object=comment.tweet, target=comment, verb='comment-like',
                    description='liked your comment')
    comment.likes.add(request.user)
    return HttpResponseRedirect(next + f'#{comment.pk}')

def unlike_comment(request, pk):
    comment = get_object_or_404(Comment, id=request.POST.get('comment_id'))
    next = request.POST.get('next', '/')
    comment.likes.remove(request.user)
    return HttpResponseRedirect(next + f'#{comment.pk}')