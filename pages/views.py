
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, redirect
from .models import *
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login, authenticate
from django.template import loader
from django.contrib.auth.models import User
from django.shortcuts import redirect, render, get_object_or_404
from .utils import update_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth import logout as auth_logout
from validate_email import validate_email
from django.template import Context
from django.conf import settings
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage
from django.http import HttpResponse, HttpResponseRedirect
import json
import requests
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.utils.timesince import timesince

MAILCHIMP_API_KEY = settings.MAILCHIMP_API_KEY
MAILCHIMP_DATA_CENTER = settings.MAILCHIMP_DATA_CENTER
MAILCHIMP_EMAIL_LIST_ID = settings.MAILCHIMP_EMAIL_LIST_ID

api_url = f'https://{MAILCHIMP_DATA_CENTER}.api.mailchimp.com/3.0'
members_endpoint = f'{api_url}/lists/{MAILCHIMP_EMAIL_LIST_ID}/members'
def subscribe(email, username):
    data = {
        "email_address":email,
        "status":"subscribed",
    }

    r = requests.post(
        members_endpoint,
        auth=("", MAILCHIMP_API_KEY),
        data = json.dumps(data)
        )


emails = list(set(User.objects.all().values_list('email', flat=True)))
usernames = list(set(User.objects.all().values_list('username', flat=True)))
def auth(request):
    if request.method == "POST" and "login-form" in request.POST:
        user = request.POST.get("username")
        passw = request.POST.get("password")
        if user in usernames:
            if user and passw:
                try:
                    userr = authenticate(username=user, password=passw)
                    if user is not None:
                        login(request, userr)
                except:
                    msg = f"Can't login with: [{user}]\nPlease make sure you're using the right password."
                    messages.success(request, msg)
                    HttpResponseRedirect(request.path)
        else:
            msg = f"Can't login with: [{user}]\n No account with this username!"
            messages.success(request, msg)
            HttpResponseRedirect(request.path)
    elif request.method == "POST" and "signup-form" in request.POST:
        user = request.POST.get("username")
        email = request.POST.get("email")
        passw = request.POST.get("password")
        message={"stat":"error" ,"message":"This username exists!"}
        if user in usernames:
            return JsonResponse(message)
        elif email in emails:
            return JsonResponse({"stat":"error" ,"message":"This email exists!"})
        elif email:
            is_valid = validate_email(email_address=email)
            if is_valid:
                new_user = User.objects.create_user(user, email, passw)
                new_user.save()
                new_author, created = Author.objects.get_or_create(fullname=user, user=new_user)
                new_author.save()
                userr = authenticate(username=user, password=passw)
                if user is not None:
                    #subscribe(email, user)
                    login(request, userr)
            else:
                return JsonResponse({"stat":"error" ,"message":"This email is not valid!"})
  
    elif request.method == "POST" and "contact" in request.POST:
        message = request.POST.get("message")
        username = request.POST.get("username")
        email = request.POST.get("email")
        from django.core.mail import EmailMessage

        emaill = EmailMessage(
            subject = username+" from SelmiTech",
            body = message,
            from_email = settings.EMAIL_HOST_USER,
            to = [settings.EMAIL_HOST_USER],
            reply_to = [email],
        )
        emaill.send()
        msg = f"Thanks! I'll respond to [{email}] ASAP."
        messages.success(request, msg)
        HttpResponseRedirect(request.path) 

def logout(request):
    auth_logout(request)
    return redirect("home")


def home(request):
    if request.method == "POST" and "signin-form" in request.POST:
        user = request.POST.get("username")
        passw = request.POST.get("password")
        if user and passw:
            try:
                userr = authenticate(username=user, password=passw)
                if user is not None:
                    login(request, userr)
                    return JsonResponse({"stat":"success" ,"message":f"Welcome {userr.username}."})
            except:
                if user not in usernames:
                    return JsonResponse({"stat":"error" ,"message":"This username is not valid!"})
                else:
                    return JsonResponse({"stat":"error" ,"message":"Please use the right password!"})

    elif request.method == "POST" and "signup-form" in request.POST:
        user = request.POST.get("username")
        email = request.POST.get("email")
        passw = request.POST.get("password")
        message={"stat":"error" ,"message":"This username exists!"}
        if user in usernames:
            return JsonResponse(message)
        elif email in emails:
            return JsonResponse({"stat":"error" ,"message":"This email exists!"})
        elif email:
            is_valid = validate_email(email_address=email)
            if is_valid:
                new_user = User.objects.create_user(user, email, passw)
                new_user.save()
                new_author, created = Author.objects.get_or_create(fullname=user, user=new_user)
                new_author.save()
                userr = authenticate(username=user, password=passw)
                if user is not None:
                    #subscribe(email, user)
                    login(request, userr)
                    return JsonResponse({"stat":"success" ,"message":f"Welcome {userr.username}."})
            else:
                return JsonResponse({"stat":"error" ,"message":"This email is not valid!"})
  
    elif request.method == "POST" and "contact" in request.POST:
        message = request.POST.get("message")
        username = request.POST.get("username")
        email = request.POST.get("email")
        

        emaill = EmailMessage(
            subject = username+" from SelmiTech",
            body = message,
            from_email = settings.EMAIL_HOST_USER,
            to = [settings.EMAIL_HOST_USER],
            reply_to = [email],
        )
        emaill.send()
        msg = f"Thanks! I'll respond to [{email}] ASAP."
        messages.success(request, msg)
        HttpResponseRedirect(request.path) 
    posts = Post.objects.all().filter(approved=True).order_by("-date")
    paginator = Paginator(posts, 9)
    page = request.GET.get("page")
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages) 

    context = {
        "posts":posts,
        "title": "blog posts"
    }

    return render(request, "blog.html", context)

def detail(request, slug):
    if request.method == "POST" and "delete-comment" in request.POST:
        comment = Comment.objects.get(id=request.POST.get("delete-comment-id"))
        comment.delete()
        return JsonResponse({"stat":"success" ,"message":f"{comment.content}: deleted."})
    if request.method == "POST" and "delete-reply" in request.POST:
        reply = Reply.objects.get(id=request.POST.get("delete-reply-id"))
        reply.delete()
        return JsonResponse({"stat":"success" ,"message":f"{reply.content}: deleted."})
    if request.method == "POST" and "signin-form" in request.POST:
        user = request.POST.get("username")
        passw = request.POST.get("password")
        if user and passw:
            try:
                userr = authenticate(username=user, password=passw)
                if user is not None:
                    login(request, userr)
                    return JsonResponse({"stat":"success" ,"message":f"Welcome {userr.username}."})
            except:
                if user not in usernames:
                    return JsonResponse({"stat":"error" ,"message":"This username is not valid!"})
                else:
                    return JsonResponse({"stat":"error" ,"message":"Please use the right password!"})

    elif request.method == "POST" and "signup-form" in request.POST:
        user = request.POST.get("username")
        email = request.POST.get("email")
        passw = request.POST.get("password")
        message={"stat":"error" ,"message":"This username exists!"}
        if user in usernames:
            return JsonResponse(message)
        elif email in emails:
            return JsonResponse({"stat":"error" ,"message":"This email exists!"})
        elif email:
            is_valid = validate_email(email_address=email)
            if is_valid:
                new_user = User.objects.create_user(user, email, passw)
                new_user.save()
                new_author, created = Author.objects.get_or_create(fullname=user, user=new_user)
                new_author.save()
                userr = authenticate(username=user, password=passw)
                if user is not None:
                    #subscribe(email, user)
                    login(request, userr)
                    return JsonResponse({"stat":"success" ,"message":f"Welcome {userr.username}."})
            else:
                return JsonResponse({"stat":"error" ,"message":"This email is not valid!"})
  
    elif request.method == "POST" and "contact" in request.POST:
        message = request.POST.get("message")
        username = request.POST.get("username")
        email = request.POST.get("email")
        msg = f"Thanks! I'll respond to [{email}] ASAP."
        messages.success(request, msg)
        HttpResponseRedirect(request.path)
    post = get_object_or_404(Post, slug=slug)
    if request.user.is_authenticated:
        author = Author.objects.get(user=request.user)
        if "comment-form" in request.POST:
            ncomment = request.POST.get("comment")
            notify_me = request.POST.get("notify-me")
            if ncomment:
                comment, created = Comment.objects.get_or_create(user=author, content=ncomment)
                if notify_me == "on":
                    msg = f"Thanks for commenting. You'll receive an email to ({author.user.email}) once you get a reply."
                    print(msg)
                    # #####HTML EMAIL###
                    data = {
                        'user': comment.user.fullname,
                        'comment':comment.content,
                        'title':post.title,
                        'url':"https://selmi.tech/post/"+post.slug
                    }

                    messagee = get_template('comment.html').render(data)

                    msgg = EmailMessage(
                        'Selmi Tech New Comment',
                        messagee,
                        settings.EMAIL_HOST_USER,
                        ['selmiabderrahim0@gmail.com'],
                    )
                    msgg.content_subtype = "html" 
                    msgg.send()


                    ###########          
                else:
                    msg = "Your comment has been submitted successfully."
                post.comments.add(comment.id)
                content = f"""
                 <div class="d-flex justify-content-center py-2">
                        <div class="second py-2 px-2"> <span class="text1">{comment}</span>
                            <div class="d-flex justify-content-between py-1 pt-2">
                                
                                <div><img src="https://cdn.pixabay.com/photo/2016/11/18/23/38/child-1837375_1280.png" width="18"><span class="text2">{comment.user.fullname}</span>
                                </div>
                                <div style="display: grid;grid-template-columns: 5fr 1fr;">
                                    <div>
                                        <span class="thumbup"></span><span class="text4">{timesince(comment.date)} ago.</span>
                                    </div>
                                </div>
                                
                            </div>
                        </div>

                    </div>
                    """
                message={"stat":"success" ,"message":msg, "content":content}
                return JsonResponse(message)
            else:
                return JsonResponse({"stat":"error" ,"message":"Please don't post an empty comment!"})
	        
        if "reply-form" in request.POST:
            reply = request.POST.get("reply")
            reply_notify_me = request.POST.get("reply-notify-me")
            if reply:
                commenr_id = request.POST.get("comment-id")
                comment_obj = Comment.objects.get(id=commenr_id)
                new_reply, created = Reply.objects.get_or_create(user=author, content=reply)
                comment_obj.replies.add(new_reply.id)
                content = f"""
                <div class="d-flex justify-content-center py-2" id="replies">
                <div class="second py-2 px-2"> <span class="text1">{new_reply.content}</span>
                    <div class="d-flex justify-content-between py-1 pt-2">
                        <div><img src="https://cdn.pixabay.com/photo/2016/11/18/23/38/child-1837375_1280.png" width="18">
                            <div style="display: grid;grid-template-columns: 5fr 1fr;">
                                <span class="text2">{new_reply.user.fullname}</span>
                            </div>
                        
                        </div>
                    </div>
                </div>
                </div>
                """
                if reply_notify_me == "on":
                    #####HTML EMAIL###
                    msg = f"Thanks for your reply. We will notify ({comment_obj.user.fullname}) about it."
                    data = {
                        'user': new_reply.user.fullname,
                        'comment':comment_obj.content,
                        'title':post.title,
                        'url':"https://selmi.tech/post/"+post.slug
                    }
                    messagee = get_template('reply.html').render(data)
                    msgg = EmailMessage(
                        'Selmi Tech New Reply',
                        messagee,
                        settings.EMAIL_HOST_USER,
                        [comment_obj.user.user.email],
                    )

                    msgg.content_subtype = "html" 
                    msgg.send()
                else:
                    msg = f"Your reply has been submitted successfully."

                message={"stat":"success" ,"message":msg, "content":content}
                return JsonResponse(message)
            else:
                return JsonResponse({"stat":"error" ,"message":"Please don't post an empty reply!"})

            ###########
    context = {
        "post":post,
        "title": post.title,
    }
    update_views(request, post)
    
    return render(request, "detail.html", context)

def category(request, slug):
    if request.method == "POST" and "signin-form" in request.POST:
        user = request.POST.get("username")
        passw = request.POST.get("password")
        if user and passw:
            try:
                userr = authenticate(username=user, password=passw)
                if user is not None:
                    login(request, userr)
                    return JsonResponse({"stat":"success" ,"message":f"Welcome {userr.username}."})
            except:
                if user not in usernames:
                    return JsonResponse({"stat":"error" ,"message":"This username is not valid!"})
                else:
                    return JsonResponse({"stat":"error" ,"message":"Please use the right password!"})

    elif request.method == "POST" and "signup-form" in request.POST:
        user = request.POST.get("username")
        email = request.POST.get("email")
        passw = request.POST.get("password")
        message={"stat":"error" ,"message":"This username exists!"}
        if user in usernames:
            return JsonResponse(message)
        elif email in emails:
            return JsonResponse({"stat":"error" ,"message":"This email exists!"})
        elif email:
            is_valid = validate_email(email_address=email)
            if is_valid:
                new_user = User.objects.create_user(user, email, passw)
                new_user.save()
                new_author, created = Author.objects.get_or_create(fullname=user, user=new_user)
                new_author.save()
                userr = authenticate(username=user, password=passw)
                if user is not None:
                    #subscribe(email, user)
                    login(request, userr)
                    return JsonResponse({"stat":"success" ,"message":f"Welcome {userr.username}."})
            else:
                return JsonResponse({"stat":"error" ,"message":"This email is not valid!"})
  
    elif request.method == "POST" and "contact" in request.POST:
        message = request.POST.get("message")
        username = request.POST.get("username")
        email = request.POST.get("email")
        from django.core.mail import EmailMessage

        emaill = EmailMessage(
            subject = username+" from SelmiTech",
            body = message,
            from_email = settings.EMAIL_HOST_USER,
            to = [settings.EMAIL_HOST_USER],
            reply_to = [email],
        )
        #emaill.send()
        msg = f"Thanks! I'll respond to [{email}] ASAP."
        messages.success(request, msg)
        HttpResponseRedirect(request.path)
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.all().filter(approved=True, categories=category).order_by("-date")
    paginator = Paginator(posts, 18)
    page = request.GET.get("page")
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages) 

    context = {
        "posts":posts,
        "title": category.title,
        "category": category,
    }
    return render(request, "category.html", context)




def search(request):
    if request.method == "POST" and "signin-form" in request.POST:
        user = request.POST.get("username")
        passw = request.POST.get("password")
        if user and passw:
            try:
                userr = authenticate(username=user, password=passw)
                if user is not None:
                    login(request, userr)
                    return JsonResponse({"stat":"success" ,"message":f"Welcome {userr.username}."})
            except:
                if user not in usernames:
                    return JsonResponse({"stat":"error" ,"message":"This username is not valid!"})
                else:
                    return JsonResponse({"stat":"error" ,"message":"Please use the right password!"})

    elif request.method == "POST" and "signup-form" in request.POST:
        user = request.POST.get("username")
        email = request.POST.get("email")
        passw = request.POST.get("password")
        message={"stat":"error" ,"message":"This username exists!"}
        if user in usernames:
            return JsonResponse(message)
        elif email in emails:
            return JsonResponse({"stat":"error" ,"message":"This email exists!"})
        elif email:
            is_valid = validate_email(email_address=email)
            if is_valid:
                new_user = User.objects.create_user(user, email, passw)
                new_user.save()
                new_author, created = Author.objects.get_or_create(fullname=user, user=new_user)
                new_author.save()
                userr = authenticate(username=user, password=passw)
                if user is not None:
                    #subscribe(email, user)
                    login(request, userr)
                    return JsonResponse({"stat":"success" ,"message":f"Welcome {userr.username}."})
            else:
                return JsonResponse({"stat":"error" ,"message":"This email is not valid!"})
  
    elif request.method == "POST" and "contact" in request.POST:
        message = request.POST.get("message")
        username = request.POST.get("username")
        email = request.POST.get("email")
        from django.core.mail import EmailMessage

        emaill = EmailMessage(
            subject = username+" from SelmiTech",
            body = message,
            from_email = settings.EMAIL_HOST_USER,
            to = [settings.EMAIL_HOST_USER],
            reply_to = [email],
        )
        #emaill.send()
        msg = f"Thanks! I'll respond to [{email}] ASAP."
        messages.success(request, msg)
        HttpResponseRedirect(request.path)
    context = {}
    if "search" in request.GET:
        query = request.GET.get("q")
        posts = Post.objects.all().filter(approved=True).order_by("-date")
        objects = posts.filter(title__icontains=query, overview__icontains=query)
        paginator = Paginator(objects, 18)
        page = request.GET.get("page")
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages) 

        context = {
            "posts":posts,
            "title": "Search",
            "query": query,
        }
    return render(request, "search.html", context)
