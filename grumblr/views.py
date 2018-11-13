from django.shortcuts import *
import datetime

# Manually create HttpResponse and Http404
from django.http import HttpResponse, Http404, JsonResponse

# Manually create and login a user
from django.contrib.auth import authenticate, login, logout

# Decorator
from django.contrib.auth.decorators import login_required
from django.db import transaction

# Send mail from within Django
from django.core.mail import send_mail
from django.core import serializers

# Helper function to guess a MIME type from a file name
from mimetypes import guess_type

from django.core.exceptions import ObjectDoesNotExist

from grumblr.models import *
from grumblr.forms import *
from django.contrib.auth.tokens import default_token_generator
# Create your views here.
import os

def index(request):
    return redirect('/grumblr/login/')


def log_in(request):
    context = {}
    if request.user.is_authenticated:
        return redirect(reverse('home', args=[request.user.username]))

    if request.method == 'GET':
        login_form = LoginForm()
        context['form'] = login_form
        return render(request, 'grumblr/login.html', context)

    login_form = LoginForm(request.POST)
    context['form'] = login_form
    if not login_form.is_valid():
        return render(request, 'grumblr/login.html', context)

    errors = []
    username = login_form.cleaned_data['username']
    password = login_form.cleaned_data['password']

    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect(reverse('home', args=[username]))
    else:
        errors.append('Invalid username and password')
        context['errors'] = errors
        return render(request, 'grumblr/login.html', context)


def register(request):
    context = {}

    if request.method == 'GET':
        register_form = RegisterForm()
        context["form"] = register_form
        return render(request, 'grumblr/register.html', context)

    register_form = RegisterForm(request.POST)
    context["form"] = register_form
    if not register_form.is_valid():
        return render(request, 'grumblr/register.html', context)

    cleaned_data = register_form.cleaned_data

    new_user = User.objects.create_user(username=cleaned_data['username'],
                                        password=cleaned_data['password'],
                                        first_name=cleaned_data['first_name'],
                                        last_name=cleaned_data['last_name'],
                                        email=cleaned_data['email'])
    new_user.is_active = False
    new_user.save()

    token = default_token_generator.make_token(new_user)
    new_profile = UserProfile(user=new_user, token_reg=token)
    new_profile.save()

    email_body = """
    Welcome to Grumblr! Please click the link below to verify your email address and complete the registration of your account:
    http://%s%s
    """ % (request.get_host(), reverse('confirm_reg', args=(new_user.username, token)))

    send_mail(subject="Verify your email address",
              message=email_body,
              from_email="no-reply@grumblr.com",
              recipient_list=[new_user.email])

    text = "Please use the link we send to your email to complete your registration."

    return render(request, 'grumblr/wait.html', {'text': text})


@transaction.atomic
def confirm_registration(request, username, token):
    context = {}

    confirm_user_profile = get_object_or_404(UserProfile, user__username=username)
    if token != confirm_user_profile.token_reg:
        User.objects.filter(username=username).delete()
        context['error'] = "Your link was expired!"
        return render(request, 'grumblr/register_conf.html', context)

    try:
        new_user = User.objects.get(username=username)
    except User.DoesNotExist:
        context['error'] = "User doesn't exist!"
        return render(request, 'grumblr/register_conf.html', context)

    new_user.is_active = True
    new_user.save()
    if len(UserProfile.objects.filter(user=new_user)) == 0:
        new_user_profile = UserProfile(user=new_user)
        new_user_profile.save()

    login(request, new_user)

    context['text'] = "Congratulations! Click the button below to go to your home page."
    context['username'] = new_user.username
    return render(request, 'grumblr/register_conf.html', context)


@login_required
def home(request, username):
    context = {}
    main_user = UserProfile.objects.get(user_id=request.user.id)
    if request.method == 'POST':
        new_message = Message(user_profile=main_user)
        message_form = MessageForm(request.POST, instance=new_message)
        if message_form.is_valid():
            message_form.save()

    message_form = MessageForm()
    user_profile = get_object_or_404(UserProfile, user__username=username)
    messages = Message.objects.filter(user_profile=user_profile).order_by('-time')

    context['user_profile'] = user_profile
    context['main_user'] = main_user
    context['messages'] = messages
    context['form'] = message_form
    context['friends'] = main_user.friends.all()
    context['is_friend'] = main_user.friends.filter(user__username=username)
    return render(request, 'grumblr/home.html', context)


@login_required
def follower(request):
    context = {}
    user_profile = UserProfile.objects.get(user_id=request.user.id)
    friends = user_profile.friends.all()
    favs = Favorite.objects.filter(user_profile=user_profile).order_by('-time')

    messages = Message.objects.filter(user_profile__in=friends).order_by('-time')
    context['user_profile'] = user_profile
    context['messages'] = messages
    context['favs'] = favs
    context['form'] = MessageForm()
    context['friends'] = friends
    return render(request, 'grumblr/follower.html', context)


@login_required
@transaction.atomic
def glob(request):
    context = {}
    user_profile = UserProfile.objects.get(user_id=request.user.id)

    if request.method == 'POST':
        new_message = Message(user_profile=user_profile)
        message_form = MessageForm(request.POST, instance=new_message)
        if message_form.is_valid():
            message_form.save()

    favs = Favorite.objects.filter(user_profile=user_profile).order_by('-time')
    context['user_profile'] = user_profile
    context['favs'] = favs
    context['form'] = MessageForm()
    context['friends'] = user_profile.friends.all()
    return render(request, 'grumblr/global.html', context)


@login_required
def global_posts(request):
    max_time = Message.get_max_time()
    messages = Message.get_changes().order_by('-time')
    context = {"messages": messages, "max_time": max_time, "user": request.user.username}
    return render(request, 'grumblr/update_messages.json', context, content_type='application/json')


@login_required
def global_update(request, time):
    max_time = Message.get_max_time()
    update_messages = Message.get_changes(time)
    context = {"messages": update_messages, "max_time": max_time, "user": request.user.username}
    return render(request, 'grumblr/update_messages.json', context, content_type='application/json')


@login_required
@transaction.atomic
def add_comment(request, id):
    message = get_object_or_404(Message, id=id)
    user_profile = get_object_or_404(UserProfile, user_id=request.user.id)

    if 'comment' not in request.POST or not request.POST['comment']:
        raise Http404

    new_comment = Comment(message=message, user_profile=user_profile, content=request.POST['comment'])
    new_comment.save()

    return HttpResponse()


@login_required
@transaction.atomic
def get_comment(request, id):
    message = get_object_or_404(Message, id=id)

    comments = Comment.objects.filter(message=message)
    context = {'comments': comments, 'id': id}
    return render(request, 'grumblr/comments.json', context, content_type='application/json')


@login_required
@transaction.atomic
def edit(request, username):
    context = {}

    if request.user.username != username:
        return redirect(reverse('home', args=[request.user.username]))

    user_profile = get_object_or_404(UserProfile, user_id=request.user.id)
    user = user_profile.user
    context['username'] = username

    if request.method == 'GET':
        profile_from = UserProfileForm(instance=user_profile)
        user_form = UserForm(instance=user)
        context['profile_form'] = profile_from
        context['user_form'] = user_form
        return render(request, 'grumblr/edit_profile.html', context)

    profile_from = UserProfileForm(request.POST, request.FILES, instance=user_profile)
    user_form = UserForm(request.POST, instance=user)
    context['profile_form'] = profile_from
    context['user_form'] = user_form

    if not profile_from.is_valid() or not user_form.is_valid():
        return render(request, 'grumblr/edit_profile.html', context)

    user_profile.save()
    user_form.save()

    return redirect(reverse('home', args=(username,)))


@login_required
@transaction.atomic
def delete_post(request, id):
    errors = []

    try:
        msg_to_delete = Message.objects.get(id=id)
        msg_to_delete.delete()
    except ObjectDoesNotExist:
        errors.append('The item did not exist in the todo list.')

    return redirect(reverse('home', args=[request.user.username]))


@login_required
@transaction.atomic
def add_fav(request, id):

    if len(Favorite.objects.filter(user_profile__user_id=request.user.id, message_id=id)) > 0:
        return redirect(reverse('global'))

    user_profile = UserProfile.objects.get(user_id=request.user.id)
    add_msg = Message.objects.get(id=id)

    new_fav = Favorite(user_profile=user_profile,
                       content=add_msg.content,
                       poster=add_msg.user_profile.user.username,
                       message_id=add_msg.id)
    new_fav.save()

    return redirect(reverse('global'))


@login_required
@transaction.atomic
def delete_fav(request, id):
    errors = []

    try:
        fav_to_delete = Favorite.objects.get(id=id)
        fav_to_delete.delete()
    except ObjectDoesNotExist:
        errors.append('The item did not exist in the todo list.')

    return redirect(reverse('global'))


@login_required
@transaction.atomic
def follow(request, username):
    main_user = UserProfile.objects.get(user_id=request.user.id)
    friend = get_object_or_404(UserProfile, user__username=username)
    main_user.friends.add(friend)
    return redirect(reverse('home', args=[username]))


@login_required
@transaction.atomic
def unfollow(request, username):
    main_user = UserProfile.objects.get(user_id=request.user.id)
    friend = get_object_or_404(UserProfile, user__username=username)
    main_user.friends.remove(friend)
    return redirect(reverse('home', args=[username]))


@login_required
def get_photo(request, username):
    user_profile = get_object_or_404(UserProfile, user__username=username)
    if not user_profile.picture:
        raise Http404

    content_type = guess_type(user_profile.picture.name)
    return HttpResponse(user_profile.picture, content_type=content_type)


@login_required
def get_header(request, username):
    user_profile = get_object_or_404(UserProfile, user__username=username)
    if not user_profile.header_photo:
        raise Http404

    content_type = guess_type(user_profile.header_photo.name)
    return HttpResponse(user_profile.header_photo, content_type=content_type)


@login_required
def reset_password_request(request):
    user = User.objects.get(username=request.user.username)

    token = default_token_generator.make_token(user)
    user_profile = UserProfile.objects.get(user__username=request.user.username)
    user_profile.token_reg = token

    email_body = """
    Please click the link below to reset your password:

    http://%s%s
    """ % (request.get_host(), reverse('confirm_pwd', args=(user.username, token)))

    send_mail(subject="Verify your email address",
              message=email_body,
              from_email="no-reply@grumblr.com",
              recipient_list=[user.email])

    user.is_active = False
    user.save()
    user_profile.save()
    logout(request)
    text = "Please use the link we send to your email to reset your password."
    return render(request, 'grumblr/wait.html', {'text': text})


def confirm_password(request, username, token):
    context = {'username': username, 'token': token}

    confirm_user_profile = get_object_or_404(UserProfile, user__username=username)
    if token != confirm_user_profile.token_reg:
        User.objects.filter(username=username).delete()
        context['error'] = "Your link was expired!"
        return render(request, 'grumblr/register_conf.html', context)

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        context['error'] = "User doesn't exist!"
        return render(request, 'grumblr/register_conf.html', context)

    if request.method == 'GET':
        reset_form = ResetForm()
        context["form"] = reset_form
        return render(request, 'grumblr/reset_pwd.html', context)

    reset_form = ResetForm(request.POST)
    context["form"] = reset_form
    if not reset_form.is_valid():
        return render(request, 'grumblr/reset_pwd.html', context)

    cleaned_data = reset_form.cleaned_data

    user.set_password(cleaned_data['password'])
    user.is_active = True
    user.save()

    login(request, user)
    return redirect(reverse('home', args=(user.username,)))


@login_required
def log_out(request):
    logout(request)
    return redirect(reverse('login'))

