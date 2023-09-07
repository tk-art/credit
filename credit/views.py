from django.shortcuts import render
from .forms import SignupForm, ProfileForm, PostForm
from .models import CustomUser, Profile, Post, Like
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
import pytz
from datetime import datetime
from django.http import JsonResponse


def human_readable_time_from_utc(timestamp, timezone='Asia/Tokyo'):
    local_tz = pytz.timezone(timezone)
    local_now = datetime.now(local_tz)
    local_timestamp = timestamp.astimezone(local_tz)
    delta = local_now - local_timestamp

    seconds = int(delta.total_seconds())
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    if days > 0:
        return f"{days}日前"
    elif hours > 0:
        return f"{hours}時間前"
    elif minutes > 0:
        return f"{minutes}分前"
    else:
        return "たった今"


def top(request):
  posts = Post.objects.all().order_by('-timestamp')
  follows_posts = None
  if request.user.is_authenticated:
    follows_profiles = request.user.profile.follows.all()
    follows_posts = Post.objects.filter(user__profile__in=follows_profiles).order_by('-timestamp')
  for post in posts:
    post.delta = human_readable_time_from_utc(post.timestamp)
  context = {
    'posts': posts,
    'follows_posts': follows_posts,
  }
  return render(request, 'top.html', context)

def signup(request):
  if request.method == 'POST':
    form = SignupForm(request.POST)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        email = form.cleaned_data.get('email')
        hash_password = make_password(form.cleaned_data.get('password'))

        user = CustomUser.objects.create(username=username, email=email, password=hash_password)

        Profile.objects.create(user=user, username=username,
                                       content='これはデフォルトのプロフィールです。好みに応じて編集してください')

        login(request, user)
        return redirect('profile', user_id=user.id)

  else:
    form = SignupForm()
  return render(request, 'signup.html', {'form': form})

def login_view(request):
    error_message = ""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('top')
        else:
            error_message = 'ユーザーネームかパスワードが違います、もう一度お試しください'

    return render(request, 'login.html', {'error_message': error_message})


def logout_view(request):
    logout(request)
    return redirect('top')


def profile(request, user_id):
    profile = get_object_or_404(Profile, user=user_id)
    posts = Post.objects.filter(user_id=user_id).order_by('-timestamp')
    follows_profiles = profile.follows.all()
    followed_profiles = profile.followed_by.all()
    is_following = request.user.profile.follows.filter(id=profile.id).exists()

    for post in posts:
      post.delta = human_readable_time_from_utc(post.timestamp)
    context = {
      'posts': posts,
      'profile': profile,
      'follows_profiles': follows_profiles,
      'followed_profiles': followed_profiles,
    }
    return render(request, 'profile.html', context)

@login_required
def profile_edit(request):
    if request.method == 'POST':
      form = ProfileForm(request.POST, request.FILES)
      if form.is_valid():
        profile_data = form.cleaned_data
        profile = Profile.objects.filter(user=request.user).first()
        if profile:
            profile.username = profile_data['username']
            profile.image = profile_data['image']
            profile.backimage = profile_data['backimage']
            profile.content = profile_data['content']
            profile.save()
        else:
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
        return redirect('profile', user_id=request.user.id)
    else:
        form = ProfileForm()
    return render(request,'profile.html', {'form' : form})

def post(request):
    form = PostForm()

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            period = form.cleaned_data['period']
            content = form.cleaned_data['content']
            image = form.cleaned_data.get('image', None)

            Post.objects.create(user=request.user, period=period, image=image, content=content)

            return redirect('top')
    return render(request, 'top.html', {'form': form})

def get_like_status(request):
    posts = Post.objects.all()
    response_data = {}
    for post in posts:
        post.is_liked = Like.objects.filter(user=request.user, post=post).exists()
        response_data[post.id] = post.is_liked

    return JsonResponse(response_data)

def like_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post, is_liked=True)

    if created:
        post.like_count += 1
        is_liked = True

    else:
        like.delete()
        post.like_count -= 1 if post.like_count > 0 else 0
        is_liked = False

    post.save()

    response_data = {
      'is_liked': is_liked,
      'like_count': post.like_count
    }
    return JsonResponse(response_data)

def follow(request, user_id):
    try:
        user_to_toggle = CustomUser.objects.get(id=user_id)
        is_following = False
        if request.user.profile.follows.filter(id=user_to_toggle.profile.id).exists():
            request.user.profile.follows.remove(user_to_toggle.profile)
        else:
            request.user.profile.follows.add(user_to_toggle.profile)
            is_following = True
        response_data = {
            'success': True,
            'is_following': is_following
        }
    except User.DoesNotExist:
        pass

    return JsonResponse(response_data)

def get_follow_status(request, user_id):
    user_to_toggle = CustomUser.objects.get(id=user_id)
    follow_status = request.user.profile.follows.filter(id=user_to_toggle.profile.id).exists()
    return JsonResponse({'success': follow_status})

def evidence(request):
    if request.method == 'POST':
        form = EvidenceForm(request.POST, request.FILES)
        if form.is_valid():
            evidence = form.save(commit=False)
            evidence.user = request.user
            evidence.save()
            if request.FILES.getlist('image[]'):
              images = request.FILES.getlist('image[]')
              for image in images:
                  EvidenceImage.objects.create(evidence=evidence, image=image)
            return redirect('profile')
    else:
        form = PostForm()
    return render(request, 'top.html', {'form': form})
