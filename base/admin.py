from django.contrib import admin
from django.contrib.admin.decorators import register
from base.models import *

@register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']


@register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author','published_date', 'updated_date', 'is_published' ]
    list_display_links = ['title', 'category', 'author','published_date', 'updated_date', 'is_published' ]


@register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'user', 'content', 'posted_on', 'visible']
    list_display_links = ['post', 'user', 'content', 'posted_on', 'visible']


