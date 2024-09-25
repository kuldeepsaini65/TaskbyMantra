from django.db import models
from django.utils.text import slugify
from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.search import SearchVector

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, help_text="Please keep it Blank for Auto Url", blank=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

from django.contrib.postgres.search import SearchVector

class Post(models.Model):
    title = models.CharField(max_length=200)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField()
    thumbnail = models.ImageField(upload_to='media/blogs/images')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    published_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    
    slug = models.SlugField(max_length=200, unique=True, help_text="Please keep it Blank for Auto Url", blank=True)

    # The search vector field for full-text search
    search_vector = SearchVectorField(null=True, blank=True)

    class Meta:
        ordering = ['-published_date']
        verbose_name_plural = 'Posts'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        # Automatically populate the search_vector field
        self.search_vector = SearchVector('title', 'content')  # Creating a search vector for title and content

        super().save(*args, **kwargs)

        
        
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    posted_on = models.DateTimeField(auto_now_add=True)
    visible = models.BooleanField(default=True, help_text="Used to Select Wheather to Show comment or not")

    class Meta:
        ordering = ['-posted_on']

    def __str__(self):
        return f'Comment by {self.user} on {self.post}'



class PostLike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    liked_on = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'Like on {self.post.title} by {self.user.username}'



class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, related_name="likes", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    liked_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('comment', 'user') 

    def __str__(self):
        return f'{self.user} likes {self.comment}'