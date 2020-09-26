import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect,JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from .models import User,Post


def index(request):
    #get all posts paginate them and orginize by reverse chrono order
    posts=Post.objects.all()
    posts=posts.order_by("-date").all()
    paginator=Paginator(posts,10)
    page_num=request.GET.get('page')
    posts=paginator.get_page(page_num)
    return render(request, "network/index.html",{
        "posts":posts
    })


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
        if "picture" in request.FILES:
           picture=request.FILES["picture"]
           fs=FileSystemStorage()
           picture_name=fs.save(picture.name,picture)

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            if "picture" in request.FILES:
               user = User.objects.create_user(username, email, password,picture=picture_name)
            else:
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

@login_required
def create_post(request):
    #Making a post must be via POST
    if request.method=="POST":
        user=User.objects.get(username__iexact=request.user)
        body=request.POST['post']
        if(body==""):
            messages.error(request,"Post cannot be empty")
        elif(len(body)<2):
            messages.error(request,"Post must have at least 2 characters")    
        elif(len(body)>500):
            messages.error(request,"Post limit is 500 characters")    
        else:
            post=Post(
                text=body,
                poster=user
            )
            post.save()
        return HttpResponseRedirect(reverse('index'))  
@csrf_exempt #not secure        
@login_required
def edit_post(request,post_id):
    #get post to update
    post=Post.objects.get(pk=post_id)
    #errors(javascript checks length errors)
    if request.method!="POST":
        return JsonResponse({"error":"POST request required."},status=400)    
    if post.poster!=request.user:
        return HttpResponse('Cannot edit another users posts') 
    #update its text 
    data=json.loads(request.body)
    text=data.get("text","")   
    post.text=text
    post.save()
    return JsonResponse({"success":'Post Updated'})  

@login_required
def delete(request,post_id):
    try:
        post=Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return HttpResponse('Post does not exist')
    if post.poster!=request.user:
        return HttpResponse('Cannot delete another users posts') 
    post.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))    

@csrf_exempt #not secure
@login_required
def like(request,post_id):
    user=User.objects.get(username__iexact=request.user)
    if request.method=="GET":#method to return all liked posts
        try:#try to get all liked posts
            liked_posts=Post.objects.filter(liked_by__username__iexact=request.user)
            return JsonResponse([liked_post.serialize() for liked_post in liked_posts],safe=False)
        except User.DoesNotExist:#user didn't like any post
            return JsonResponse([0],safe=False)


    elif request.method=="POST":#method for updating likes
        try:
            post=Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return JsonResponse({"error":"Post not found."},status=400)
        if user.liked.filter(pk=post_id):#if the post has already been liked
            user.liked.remove(post)
            post.liked_by.remove(user)
            post.likes-=1
        else:#post has not been liked
            user.liked.add(post)
            post.liked_by.add(user)
            post.likes+=1   
        post.save()
        return JsonResponse([post.likes],safe=False)

    else:
        return JsonResponse({"error":"GET or PUT request required."},status=400)


@login_required
def profile(request,username):
    #get user posts 
    posts=Post.objects.filter(poster__username=username)
    posts=posts.order_by("-date").all()
    paginator=Paginator(posts,10)
    page_num=request.GET.get('page')
    posts=paginator.get_page(page_num)

    #get counters for user profile
    user=User.objects.get(username__iexact=username)
    followers=user.followers.all().count()
    following=user.following.all().count()
    posts_cnt=Post.objects.filter(poster__username=username).count()
    if request.user.username!=username:
        follow_flag=1
    else:
        follow_flag=0    
    context={
        "follow_flag":follow_flag,
        "posts":posts,
        "user_profile":user,
        "posts_cnt":posts_cnt,
        "followers":followers,
        "following":following}
    return render(request,"network/profile.html",context)
    
@csrf_exempt
@login_required
def follow(request,username,mission):
    if request.method=='GET':#method to check if the user we are viewing is followed by the logged in user
        try:
            User.objects.filter(following__username=username).get(username__iexact=request.user)#check if the logged in user is following the users profile
            return JsonResponse([1],safe=False)
        except User.DoesNotExist:#means user is not followed
            return JsonResponse([0],safe=False)

    elif request.method=='POST':#method to follow or unfollow a user
        user_follow=User.objects.get(username__iexact=username)#user to follow
        user_follower=User.objects.get(username__iexact=request.user)#user that follows
        if(mission=="follow"):
            user_follow.followers.add(user_follower)
            user_follower.following.add(user_follow)
        else:#unfollow
            user_follow.followers.remove(user_follower)
            user_follower.following.remove(user_follow)
        followers=user_follow.followers.count()#count the updated follower count
        return JsonResponse([followers],safe=False)
    else:
        return JsonResponse({"error":"GET or PUT request required."},status=400)

@login_required
def following(request):
    user=User.objects.get(username__iexact=request.user)
    following=user.following.all().values('username')#get all followed usernames
    posts=Post.objects.filter(poster__username__in=following)#get all posts from followed users
    posts=posts.order_by("-date").all()#chrono order
    #pagination
    paginator=Paginator(posts,10)
    page_num=request.GET.get('page')
    posts=paginator.get_page(page_num)

    return render(request,'network/following.html',{
        "posts":posts
    })