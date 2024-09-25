from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.contrib.auth import login
from .models import *
from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from base.models import *
from django.contrib import messages
from django.core.mail import send_mail
from django.views import View
from base.models import Post, Category, PostLike, Comment
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.postgres.search import SearchVector, SearchRank, SearchQuery, TrigramSimilarity
from .forms import *
from django.db.models import Value
from django.template.loader import render_to_string
from django.http import JsonResponse



def SignIn(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            user = authenticate(request, username=username, password=password)
        except Exception as e:
            print(e)

        if user is not None:
            login(request, user)
            messages.success(request,"Login Successfully !")
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'login.html')



def SignUp(request):
    if request.method == 'POST':
        first_name = request.POST.get('fname')
        last_name = request.POST.get('lname')
        username = request.POST.get('username')
        password = request.POST.get('password')
                
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('SignUp')

        else:
            user = User.objects.create_user(
                    username=username,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
            )
            user.save()
            login(request, user)
            messages.success(request,  "Account Creation Done")
            return redirect('home')  
        

    return render(request, 'signup.html')


def LogOut(request):
    logout(request)
    messages.success(request,"Log Out Successfully")
    return redirect('SignIn')


 
class Home(View):
    def get(self, request, *args, **kwargs):
        search_form = SearchForm(request.GET or None)
        query = None
        posts = Post.objects.filter(is_published=True).order_by('-published_date')

        if search_form.is_valid():
            query = search_form.cleaned_data.get('query')

            if query:
                search_query = SearchQuery(query)
                search_vector = SearchVector('title', 'content')
                full_text_posts = Post.objects.annotate(
                    search=search_vector,
                    rank=SearchRank(search_vector, search_query),
                    trigram_sim=TrigramSimilarity('title', query),
                ).filter(search=search_query).order_by('-rank', '-trigram_sim')

                full_text_posts = full_text_posts.values(
                    'id', 'title', 'content', 'published_date', 'author', 'rank', 'slug', 'thumbnail'
                )

                similar_posts = Post.objects.annotate(
                    trigram_sim=TrigramSimilarity('slug', query)
                ).filter(trigram_sim__gt=0.3).values(
                    'id', 'title', 'content', 'published_date', 'author', 'slug', 'thumbnail'
                )

                similar_posts = similar_posts.annotate(rank=Value(0))

                combined_posts = full_text_posts.union(similar_posts).order_by('-rank')

                paginator = Paginator(combined_posts, 5)
                page = request.GET.get('page')

                try:
                    paginated_posts = paginator.page(page)
                except PageNotAnInteger:
                    paginated_posts = paginator.page(1)
                except EmptyPage:
                    paginated_posts = paginator.page(paginator.num_pages)

                return render(request, 'index.html', {
                    'posts': paginated_posts,
                    'search_form': search_form,
                    'query': query
                })

       
        paginator = Paginator(posts, 5)
        page = request.GET.get('page')

        try:
            paginated_posts = paginator.page(page)
        except PageNotAnInteger:
            paginated_posts = paginator.page(1)
        except EmptyPage:
            paginated_posts = paginator.page(paginator.num_pages)

        return render(request, 'index.html', {
            'posts': paginated_posts,
            'search_form': search_form,
            'query': query
        })

        



class PostDetailView(View):
    def get(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug, is_published=True)
        comments = Comment.objects.filter(post=post, visible=True).order_by('-posted_on')
        if request.user.is_authenticated:
            user_has_liked = PostLike.objects.filter(user=request.user, post=post).exists()
        else:
            user_has_liked = False
        return render(request, 'blog_details.html', {
            'post': post,
            'comments': comments,
            'user_has_liked': user_has_liked,
        })

@login_required
def toggle_like(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    post_slug = comment.post.slug

    user = request.user
    like, created = CommentLike.objects.get_or_create(user=user, comment=comment)
    if not created:
        like.delete()
    return redirect('post-detail', slug=post_slug)


@method_decorator(login_required, name='dispatch')
class PostLikeView(View):
    def post(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
        user = request.user

        like, created = PostLike.objects.get_or_create(user=user, post=post)

        if not created:
            like.delete()
        return redirect('post-detail', slug=post.slug)

class CategoryListView(View):
    def get(self, request, slug, *args, **kwargs):
        category = get_object_or_404(Category, slug=slug)
        posts = Post.objects.filter(category=category, is_published=True).order_by('-published_date')
        return render(request, 'category_posts.html', {'category': category, 'posts': posts})


@method_decorator(login_required, name='dispatch')
class AddCommentView(View):
    def post(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
        content = request.POST.get('content')
        print(request.body)
        if content:
            Comment.objects.create(post=post, user=request.user, content=content, visible=True)
            messages.success(request,  "Comment Added Successfully")
            
        else:
            print("No Content")
        return HttpResponseRedirect(reverse('post-detail', args=[slug]))



class SearchPosts(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        posts = Post.objects.filter(title__icontains=query, is_published=True).order_by('-published_date')
        
        paginator = Paginator(posts, 5)
        page = request.GET.get('page')
        
        try:
            paginated_posts = paginator.page(page)
        except PageNotAnInteger:
            paginated_posts = paginator.page(1)
        except EmptyPage:
            paginated_posts = paginator.page(paginator.num_pages)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('search_results.html', {'posts': paginated_posts})
            return JsonResponse({'html': html})

        
        return render(request, 'index.html', {'posts': paginated_posts})
    



class SharePostView(View):
    def get(self, request, post_id, *args, **kwargs):
        post = get_object_or_404(Post, id=post_id, is_published=True)
        form = EmailPostForm()
        return render(request, 'share_post.html', {'post': post, 'form': form})

    def post(self, request, post_id, *args, **kwargs):
        post = get_object_or_404(Post, id=post_id, is_published=True)
        form = EmailPostForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(reverse('post-detail', args=[post.slug]))
            subject = f"{cd['name']} recommends you read '{post.title}'"
            message = f"Read '{post.title}' at {post_url}\n\n{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, cd['email'], [cd['to']])

            return render(request, 'share_post_success.html', {'post': post, 'form': form})

        return render(request, 'share_post.html', {'post': post, 'form': form})