import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

userModel = get_user_model()

class Tweet(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    content = models.CharField(max_length=255, verbose_name='')
    author = models.ForeignKey(
        userModel,
        related_name='tweets',
        on_delete=models.CASCADE,
    )
    likes = models.ManyToManyField(userModel, related_name='tweet_likes')
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.content
    
    def get_absolute_url(self):
        return reverse('tweet_detail', args=[str(self.pk)])
    
class Comment(models.Model):
    tweet = models.ForeignKey(
        Tweet,
        related_name='comments',
        on_delete=models.CASCADE,
    )
    comment = models.CharField(max_length=140, verbose_name='')
    author = models.ForeignKey(
        userModel,
        on_delete=models.CASCADE
    )
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.comment

class UserFollowing(models.Model):
    user_id = models.ForeignKey(
        userModel,
        related_name='following',
        on_delete=models.CASCADE,
    )
    following_user_id = models.ForeignKey(
        userModel,
        related_name='followers',
        on_delete=models.CASCADE,
    )
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user_id','following_user_id'],  name="unique_followers")
        ]

        ordering = ["-created"]
        
    def __str__(self):
        return f'{self.user_id} follows {self.following_user_id}'