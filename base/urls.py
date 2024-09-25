from django.contrib import admin
from django.urls import path, include
from base.views import *


urlpatterns = [
    path('signin', SignIn, name="SignIn"),
    path('signup', SignUp, name="SignUp"),
    path('logout', LogOut, name="LogOut"),
    path('', Home.as_view(), name="home"),
    
      # Post-related URLs
    # path('posts/', PostListView.as_view(), name='post-list'),  # All posts
    path('posts/<slug:slug>/', PostDetailView.as_view(), name='post-detail'),  # Post detail view
    path('posts/<slug:slug>/like/', PostLikeView.as_view(), name='post-like'),  # Like post
    
    # Category-related URLs
    path('category/<slug:slug>/', CategoryListView.as_view(), name='category-posts'),  # View posts by category

    # Comment-related URLs
    path('posts/<slug:slug>/comment/', AddCommentView.as_view(), name='add-comment'),  # Add comment to a post
    path('search/', SearchPosts.as_view(), name='search-posts'),
     path('share/<int:post_id>/', SharePostView.as_view(), name='share-post'),
      # Like/unlike comment
    path('comment/<int:comment_id>/like/', toggle_like, name='toggle-like'),

]
