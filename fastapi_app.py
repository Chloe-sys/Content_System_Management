import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "content_management.settings")
django.setup()

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import List
from fastapi.security import OAuth2PasswordBearer
from django.contrib.auth.models import User
from content_system.models import Post, LikeDislike, PostSubscription
from users.models import User_Profile
from django.conf import settings
from datetime import datetime
from django.db.models import Count, Q

# Create FastAPI app
app = FastAPI()

# OAuth2 for authentication simulation
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Pydantic models (for request validation)
class PostIn(BaseModel):
    title: str
    overview: str = "No overview provided"
    content: str

class PostOut(BaseModel):
    id: int
    title: str
    overview: str
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True  # This allows Pydantic to work with Django models
    
    

class LikeDislikeIn(BaseModel):
    post_id: int
    liked: bool

class PostSubscriptionIn(BaseModel):
    post_id: int

# Utility function to simulate authentication (you can replace this with real logic)
def authenticate_user(token: str):
    # Simulate a token validation (for now, just check for a placeholder token)
    if not token or token != "valid_token":
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    return "authenticated_user"

# Database session dependency (uses Django's ORM)
def get_db():
    # In Django, you can access the database directly without needing a custom session management
    return models

# Endpoints
@app.post("/posts/", response_model=PostOut)
def create_post(post: PostIn, token: str = Depends(oauth2_scheme)):
    authenticate_user(token)
    
    # Create a new post in Django's database
    new_post = Post.objects.create(
        title=post.title,
        overview=post.overview,
        content=post.content
    )
    return new_post

@app.get("/posts/", response_model=List[PostOut])
def list_posts():
    # Fetch all posts from the database
    posts = Post.objects.all()
    return posts

@app.get("/posts/engagements")
def get_post_engagement():
    """
    Fetch the engagement details (likes and dislikes) for a specific post.
    """
    try:
        post_engagements = Post.objects.annotate(
                likes_count=Count("likes_dislikes", filter=Q(likes_dislikes__liked=True)),
                dislikes_count=Count("likes_dislikes", filter=Q(likes_dislikes__liked=False)),
            ).values("id", "title", "likes_count", "dislikes_count")
        # print(post_engagements[:100])
        # return {"m": 1}
        post_engagements = [{
            "post_id": post_engagement["id"],
            "title": post_engagement["title"],
            "likes": post_engagement["likes_count"],
            "dislikes": post_engagement["dislikes_count"],
        } for post_engagement in post_engagements]
        return post_engagements
    except Exception as e:
        raise HTTPException(status_code=404, detail=e.__str__())

@app.get("/posts/{post_id}", response_model=PostOut)
def get_post(post_id: int):
    # Fetch a specific post by ID
    try:
        post = Post.objects.get(id=post_id)
        # Now convert the post to the PostOut model before returning
        return post
    except Post.DoesNotExist:
        raise HTTPException(status_code=404, detail="Post not found")

@app.put("/posts/{post_id}", response_model=PostOut)
def update_post(post_id: int, post: PostIn, token: str = Depends(oauth2_scheme)):
    authenticate_user(token)
    
    # Fetch the post to update
    try:
        db_post = Post.objects.get(id=post_id)
        db_post.title = post.title
        db_post.overview = post.overview
        db_post.content = post.content
        db_post.save()
        return db_post
    except Post.DoesNotExist:
        raise HTTPException(status_code=404, detail="Post not found")

@app.delete("/posts/{post_id}")
def delete_post(post_id: int, token: str = Depends(oauth2_scheme)):
    authenticate_user(token)
    
    # Delete the post
    try:
        db_post = Post.objects.get(id=post_id)
        db_post.delete()
        return {"message": "Post deleted"}
    except Post.DoesNotExist:
        raise HTTPException(status_code=404, detail="Post not found")

@app.post("/posts/{post_id}/like", response_model=dict)
def like_post(post_id: int, like_dislike: LikeDislikeIn, token: str = Depends(oauth2_scheme)):
    authenticate_user(token)
    
    # Create or update the like/dislike record
    user = User.objects.get(username="authenticated_user")  # Replace with actual authenticated user
    post = Post.objects.get(id=post_id)
    
    like_dislike_obj, created = LikeDislike.objects.update_or_create(
        user=user, post=post,
        defaults={"liked": like_dislike.liked}
    )
    return {"message": f"Post {post_id} liked: {like_dislike.liked}"}

@app.post("/posts/{post_id}/subscribe", response_model=dict)
def subscribe_to_post(post_id: int, subscription: PostSubscriptionIn, token: str = Depends(oauth2_scheme)):
    authenticate_user(token)
    
    # Simulate subscribing to a post
    user = User.objects.get(username="authenticated_user")  # Replace with actual authenticated user
    post = Post.objects.get(id=post_id)
    
    subscription_obj, created = PostSubscription.objects.update_or_create(
        user=user, post=post
    )
    return {"message": f"User subscribed to post {post_id}"}

@app.post("/posts/{post_id}/unsubscribe", response_model=dict)
def unsubscribe_from_post(post_id: int, subscription: PostSubscriptionIn, token: str = Depends(oauth2_scheme)):
    authenticate_user(token)
    
    # Simulate unsubscribing from a post
    user = User.objects.get(username="authenticated_user")  # Replace with actual authenticated user
    post = Post.objects.get(id=post_id)
    
    subscription_obj = PostSubscription.objects.filter(user=user, post=post)
    if subscription_obj.exists():
        subscription_obj.delete()
        return {"message": f"User unsubscribed from post {post_id}"}
    else:
        raise HTTPException(status_code=404, detail="Subscription not found")

@app.get("/posts/{post_id}/engagement", response_model=dict)
def get_post_engagement(post_id: int):
    """
    Fetch the engagement details (likes and dislikes) for a specific post.
    """
    try:
        # Retrieve the post
        post = Post.objects.get(id=post_id)

        # Calculate likes and dislikes
        likes_count = LikeDislike.objects.filter(post=post, liked=True).count()
        dislikes_count = LikeDislike.objects.filter(post=post, liked=False).count()

        return {
            "post_id": post_id,
            "title": post.title,
            "likes": likes_count,
            "dislikes": dislikes_count,
        }

    except Post.DoesNotExist:
        raise HTTPException(status_code=404, detail="Post not found")

