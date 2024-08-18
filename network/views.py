from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.core.paginator import Paginator
import json, bleach, re

from .models import User, Post, Like, Follow


def index(request):
    post_list = Post.objects.all().order_by("-timestamp")
    paginator = Paginator(post_list, 10)  

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html", {'page_obj': page_obj})

#@login_required
def user_profile(request, user_id):
    profile_user = get_object_or_404(User, pk=user_id)
    post_list = Post.objects.filter(user=profile_user).order_by("-timestamp")
    paginator = Paginator(post_list, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    is_following = False
    follower_count = profile_user.followers.count()
    following_count = profile_user.following.count()

    if request.user.is_authenticated:
        is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()

    return render(request, "network/user_profile.html", {
        "profile_user": profile_user,
        "page_obj":page_obj,
        "follower_count":follower_count,
        "following_count":following_count,
        "is_following":is_following
        })

@login_required
def following(request):
    following_users = Follow.objects.filter(follower=request.user).values_list('following', flat=True)

    post_list = Post.objects.filter(user__in=following_users).order_by("-timestamp")
    paginator = Paginator(post_list, 10)  

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/following.html", {"page_obj": page_obj})

def linkify_urls(text):
    url_pattern = re.compile(r'(?<!href=")(https?://\S+)')
    return url_pattern.sub(r'<a href="\1" target="_blank">\1</a>', text)

def contains_link(content):
    # This function checks if the content already contains an <a> tag
    return bool(re.search(r'<a\s+(?:[^>]*?\s+)?href=([\"\'])(.*?)\1', content))

@login_required
def create_post(request):
    if request.method == "POST":
        content = request.POST["content"]
         # Clean the content with bleach
        cleaned_content = bleach.clean(
            content,
            tags=['a', 'b', 'i', 'strong', 'em', 'p', 'br'],
            attributes={'a': ['href', 'title', 'target']},
            protocols=['http', 'https']
        )
        # Transform URLs into clickable links
        linked_content = linkify_urls(cleaned_content)
        linked_content = linked_content.replace('\n', '<br>')
        post = Post(user=request.user, content=linked_content)
        post.save()
        return redirect("index")
    return render(request, "network/create_post.html")

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
    return JsonResponse({"likes": post.likes.count()})

@login_required
def follow_user(request, user_id):
    user_to_follow = get_object_or_404(User, id=user_id)
    follow, created = Follow.objects.get_or_create(follower=request.user, following=user_to_follow)
    if not created:
        follow.delete()
    return redirect("user_profile", user_id=user_id)

@login_required
@require_http_methods(["PUT"])
def edit_post(request, post_id):
    data = json.loads(request.body)
    new_content = data.get("content", "")
    
    try:

        # Clean the content and allow basic HTML tags
        cleaned_content = bleach.clean(
            new_content,
            tags=['a', 'b', 'i', 'strong', 'em', 'p', 'br'],
            attributes={'a': ['href', 'title', 'target']},
            protocols=['http', 'https']
        )

        if not contains_link(cleaned_content):
            # Only linkify if there are no links in the content already
            linked_content = linkify_urls(cleaned_content)
        else:
            linked_content = cleaned_content

        linked_content = linked_content.replace('\n', '<br>')

        post = Post.objects.get(id=post_id, user=request.user)
        post.content = linked_content
        post.timestamp = timezone.now()
        post.save()
        return JsonResponse({"success": True, "content": post.content,"timestamp": post.timestamp.isoformat()}, status=200)
    except Post.DoesNotExist:
        return JsonResponse({"success": False, "error": "Post not found or not authorized"}, status=404)

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
