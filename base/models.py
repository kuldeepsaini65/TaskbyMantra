from django.db import models
from django.utils.text import slugify
from django.db import models
from django.contrib.auth.models import User



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
    class Meta:
        ordering = ['-published_date']
        verbose_name_plural = 'Posts'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)



class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    posted_on = models.DateTimeField(auto_now_add=True)
    visible = models.BooleanField(default=False, help_text="Used to Select Wheather to Show comment or not")

    class Meta:
        ordering = ['-posted_on']

    def __str__(self):
        return f'Comment by {self.name} on {self.post}'



class PostLike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'Like on {self.post.title} by {self.user.username}'
