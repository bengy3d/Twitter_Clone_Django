from django import forms
from django import forms
from django.forms import ModelForm
from tweets.models import Comment, Tweet, UserFollowing

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']
        widgets = {
            'comment': forms.TextInput(
                attrs={'placeholder': 'Tweet your reply'}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(CommentForm, self).__init__(*args, **kwargs)
        
class TweetForm(ModelForm):
    class Meta:
        model = Tweet
        fields = ['content']
        widgets = {
            'content': forms.TextInput(
                attrs={'placeholder': 'What\'s on your mind?'}),
        }
        
class FollowForm(ModelForm):
    class Meta:
        model = UserFollowing
        fields = []
        
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(FollowForm, self).__init__(*args, **kwargs)