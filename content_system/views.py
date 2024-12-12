from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, LikeDislike, PostSubscription
from django.http import HttpResponse
from django.contrib import messages
from django.template import loader
from django.contrib.auth.decorators import login_required
from .forms import PostForm
from django.http import JsonResponse
import requests
from fastapi_app import app as fastapi_app
import pandas as pd


# def post_list(request):
#     template = loader.get_template('post_list.html')
#     return HttpResponse(template.render())
#     # posts = Post.objects.all()
#     # return render(request, 'content_system/post_list.html', {'posts': posts})

# Create your views here.

def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("post_list")

    else:
        form = PostForm()
    return render(request, "create_post.html", {"form": form})



def post_list(request):
    posts = Post.objects.all()
    return render(request, "post_list.html", {"posts": posts})


def update_post(request, pk):
    post = Post.objects.get(pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance = post)
        if form.is_valid():
            form.save()
            return redirect("post_list")
    else:
        form = PostForm(instance=post)
    return render(request, "update_list.html", {"form": form})


def delete_post(request, pk):
    post = Post.objects.get(pk=pk)
    if request.method == "POST":
        post.delete()
        return redirect("post_list")
    return render(request, "delete_post.html", {"post": post})



@login_required
def all_posts(request):
    posts = Post.objects.all()
    return render(request, 'content_system/all_posts.html', {'posts': posts})

# View for displaying detailed post information
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        if request.user.is_authenticated:
            # Handle subscription logic
            if 'subscribe' in request.POST:
                PostSubscription.objects.get_or_create(user=request.user, post=post)
            elif 'unsubscribe' in request.POST:
                PostSubscription.objects.filter(user=request.user, post=post).delete()

    # Check if the user is subscribed to this post
    subscribed = PostSubscription.objects.filter(user=request.user, post=post).exists() if request.user.is_authenticated else False

    return render(request, 'content_system/post_detail.html', {'post': post, 'subscribed': subscribed})


def poster_dashboard(request):
    if request.user.is_authenticated and request.user.is_poster:  # Check if the user is a poster
        posts = Post.objects.filter(author=request.user)  # Assuming you have an author field in Post
        return render(request, 'content_system/post_list.html', {'posts': posts})
    return redirect('landing')  # Redirect to landing if not authenticated

@login_required
def subscribe_to_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Check if the user is already subscribed
    if PostSubscription.objects.filter(user=request.user, post=post).exists():
        messages.warning(request, "You are already subscribed to this post.")
    else:
        # Create a new subscription
        PostSubscription.objects.create(user=request.user, post=post)
        messages.success(request, f"You have successfully subscribed to {post.title}!")

    # Redirect to the dashboard
    return redirect('dashboard')  # Ensure 'dashboard' is the name of your dashboard URL pattern
@login_required
def subscription_success(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'content_system/subscription_success.html', {'post': post})

@login_required
def topic_posts(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'content_system/post_detail.html', {'post': post})


def fetch_fastapi_posts(request):
    response = requests.get("http://127.0.0.1:8002/posts/")
    posts = response.json() if response.status_code == 200 else []
    return render(request, "fastapi_posts.html", {"posts": posts})



@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    # Try to get the existing like/dislike or create a new one if it doesn't exist
    reaction, created = LikeDislike.objects.get_or_create(post=post, user=request.user)
    
    # Toggle the like (if already liked, un-like, if not liked, like it)
    if reaction.liked:
        reaction.liked = False  # Un-like if already liked
    else:
        reaction.liked = True  # Like if not already liked
        reaction.disliked = False  # Remove dislike if liked

    reaction.save()
    return redirect('post_detail', post_id=post.id)

@login_required
def dislike_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    # Check if the user has already liked the post
    existing_like_dislike = LikeDislike.objects.filter(user=user, post=post).first()

    if existing_like_dislike:
        if existing_like_dislike.liked:  # If already liked, remove the like and add a dislike
            existing_like_dislike.liked = False
            existing_like_dislike.save()
        else:  # If already disliked, remove the dislike
            existing_like_dislike.delete()
    else:
        # If no like/dislike exists, create a new dislike
        LikeDislike.objects.create(user=user, post=post, liked=False)

    return redirect('post_detail', post_id=post.id)

def post_statistics(request, post_id):
    # Retrieve the post object
    post = get_object_or_404(Post, id=post_id)

    # Get the count of likes and dislikes for the post
    likes_count = LikeDislike.objects.filter(post=post, liked=True).count()
    dislikes_count = LikeDislike.objects.filter(post=post, liked=False).count()

    # Prepare the data to send to the front-end
    data = {
        'likes': likes_count,
        'dislikes': dislikes_count
    }

    return JsonResponse(data)



# def merged_dataset_view(request):
#     try:
#         # Load the merged dataset
#         merged_df = pd.read_csv("merged_dataset.csv")
#     except FileNotFoundError:
#         return render(request, "content_system/merged_dataset.html", {"error": "Dataset not found. Run the fetch_and_merge command."})

#     # Convert the dataset to a dictionary for rendering
#     dataset = merged_df.to_dict(orient="records")
#     columns = merged_df.columns

#     return render(request, "content_system/merged_dataset.html", {"dataset": dataset, "columns": columns})











# @login_required
# def content_list(request):
#     contents = Content.objects.filter(user=request.user)
#     return render(request, 'content/content_list.html', {'contents': contents})

# @login_required
# def content_create(request):
#     if request.method == 'POST':
#         title = request.POST['title']
#         body = request.POST['body']
#         content_type = request.POST['content_type']
#         Content.objects.create(user=request.user, title=title, body=body, content_type=content_type)
#         return redirect('content_list')
#     return render(request, 'content/content_create.html')

# @login_required
# def content_update(request, id):
#     content = get_object_or_404(Content, id=id)
#     if request.method == 'POST':
#         content.title = request.POST['title']
#         content.body = request.POST['body']
#         content.content_type = request.POST['content_type']
#         content.save()
#         return redirect('content_list')
#     return render(request, 'content/content_update.html', {'content': content})

# @login_required
# def content_delete(request, id):
#     content = get_object_or_404(Content, id=id)
#     content.delete()
#     return redirect('content_list')


