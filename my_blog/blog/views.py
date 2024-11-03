from django.shortcuts import render

from django.http import HttpResponse

from .models import Post

from django.shortcuts import get_object_or_404

from django.shortcuts import redirect

from .forms import PostForm

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse,HttpResponseForbidden

from django.core.paginator import Paginator

from .forms import CommentForm

from django.views.decorators.cache import cache_page
from django.core.cache import cache

def blog_home(request):
    return HttpResponse("Hello, Blog!")


@cache_page(60) 
def post_list(request):
    server_info = f"Served by Server 1 (8001)" if request.get_host() == "127.0.0.1:8001" else "Served by Server 2 (8002)"
    posts = Post.objects.all().order_by('-created_at').select_related('author').prefetch_related('tags')
    paginator = Paginator(posts, 5)  # 5 posts per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/post_list.html', {'page_obj': page_obj})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)

    comment_count_cache_key = f'comment_count_post_{post.pk}'
    comment_count = cache.get(comment_count_cache_key)
    
    if comment_count is None:
        comment_count = post.comments.count()
        cache.set(comment_count_cache_key, comment_count, timeout=60)

    comments = post.comments.all()
    
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()

            cache.delete(comment_count_cache_key)
            
            return redirect('post_detail', pk=post.pk)
    else:
        comment_form = CommentForm()

    return render(request, 'blog/post_detail.html', {'post': post, 'comments': comments, 'comment_form': comment_form})

@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_form.html', {'form': form})

@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user != post.author:
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post_detail', pk=post.pk)
    else:
        initial_tags = ', '.join([tag.name for tag in post.tags.all()])
        form = PostForm(instance=post, initial={'tags': initial_tags})
    return render(request, 'blog/post_form.html', {'form': form})

@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user != post.author:
        return HttpResponseForbidden()

    if request.method == 'POST':
        post.delete()
        return redirect('post_list')
    return render(request, 'blog/post_confirm_delete.html', {'post': post})


from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib import messages

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully!')
            return redirect('login')
    else:
        form = RegisterForm()
    
    return render(request, 'blog/register.html', {'form': form})


def optimized_post_list(request):
    posts = Post.objects.all().prefetch_related('comments').select_related('author')
    return render(request, 'blog/optimized_post_list.html', {'posts': posts})

DEBUG = True
from django.db import connection

def optimized_post_list_second(request):
    posts = Post.objects.all().prefetch_related('comments').select_related('author')
    for post in posts:
        print(post.title, post.author.username)
        for comment in post.comments.all():
            print('-', comment.content)
    print(connection.queries)
    return render(request, 'blog/optimized_post_list.html', {'posts': posts})

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import KeyValueStore
from .serializers import KeyValueStoreSerializer

import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
def store_key_value(request):
    serializer = KeyValueStoreSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        logger.debug("Key Value Get request")
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def retrieve_value(request, key):
    try:
        key_value = KeyValueStore.objects.get(key=key)
        serializer = KeyValueStoreSerializer(key_value)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except KeyValueStore.DoesNotExist:
        return Response({"error": "Key not found"}, status=status.HTTP_404_NOT_FOUND)
    


import requests

INSTANCES = ["http://localhost:8001", "http://localhost:8002", "http://localhost:8003"]

def quorum_write(key, value, version):
    confirmations = 0
    for instance in INSTANCES:
        try:
            response = requests.post(f"{instance}/store/", json={"key": key, "value": value, "version": version})
            if response.status_code == 201:
                confirmations += 1
            if confirmations >= (len(INSTANCES) // 2) + 1:
                return True
        except requests.RequestException:
            continue
    return False

def quorum_read(key):
    responses = []
    for instance in INSTANCES:
        try:
            response = requests.get(f"{instance}/retrieve/{key}/")
            if response.status_code == 200:
                responses.append(response.json())
        except requests.RequestException:
            continue
    if responses:
        return max(responses, key=lambda x: x.get("version", 0))
    return None
