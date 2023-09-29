from django.shortcuts import render
from .forms import SignupForm, ProfileForm, PostForm, EvidenceForm, EvidenceImageForm, EvidenceRatingForm
from .models import CustomUser, Profile, Post, Like, Evidence, EvidenceImage, EvidenceRating, Notification
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
import pytz
from datetime import datetime
from django.http import JsonResponse
from django.db.models import Avg
from django.core.paginator import Paginator

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
    for post in follows_posts:
        post.formatted_deadline = post.deadline.strftime('%Y-%m-%d %H:%Mまで')
        if hasattr(post, 'evidence'):
            post.evidence.delta = human_readable_time_from_utc(post.evidence.timestamp)
  for post in posts:
    post.delta = human_readable_time_from_utc(post.timestamp)
    post.formatted_deadline = post.deadline.strftime('%Y-%m-%d %H:%Mまで')
    if hasattr(post, 'evidence'):
      post.evidence.delta = human_readable_time_from_utc(post.evidence.timestamp)
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

def calculate_achievement_rate(user):
    posts = Post.objects.filter(user=user)
    on_time_submissions = 0

    for post in posts:
        if hasattr(post, 'evidence'):
            evidence = post.evidence
            if evidence and evidence.timestamp <= post.deadline:
                on_time_submissions += 1

    if not posts:
        return 0

    return (on_time_submissions / len(posts)) * 100

def avg_rating(user):
    evidences = Evidence.objects.filter(user=user)

    avg_ratings = 0
    for evidence in evidences:
        evidence_rate = EvidenceRating.objects.filter(evidence_id=evidence.id)
        if evidence_rate.exists():
          average_rating = evidence_rate.aggregate(Avg('star_count'))
          rounded_avg = round(average_rating['star_count__avg'], 1)
          avg_ratings += rounded_avg
        else:
            rounded_avg = 0

    if len(evidences) == 0:
        ratin = 0
    else:
        ratin = avg_ratings / len(evidences)

    return ratin


def profile(request, user_id):
    user = CustomUser.objects.get(pk=user_id)
    profile = get_object_or_404(Profile, user=user_id)
    posts = Post.objects.filter(user_id=user_id).order_by('-timestamp')
    follows_profiles = profile.follows.all()
    followed_profiles = profile.followed_by.all()
    is_following = request.user.profile.follows.filter(id=profile.id).exists()
    evidences = Evidence.objects.filter(user=user_id).order_by('-timestamp')

    for evidence in evidences:
      evidence.delta = human_readable_time_from_utc(evidence.timestamp)
      evidence.post.delta = human_readable_time_from_utc(evidence.post.timestamp)
      evidence_rate = EvidenceRating.objects.filter(evidence_id=evidence.id)


    for post in posts:
      post.delta = human_readable_time_from_utc(post.timestamp)
      post.formatted_deadline = post.deadline.strftime('%Y-%m-%d %H:%Mまで')
      if hasattr(post, 'evidence'):
        post.evidence.delta = human_readable_time_from_utc(post.evidence.timestamp)

    rate = round(calculate_achievement_rate(user), 1)
    ratin = avg_rating(user)


    context = {
      'posts': posts,
      'profile': profile,
      'follows_profiles': follows_profiles,
      'followed_profiles': followed_profiles,
      'evidences': evidences,
      'rate': rate,
      'ratin': ratin,
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
            post = form.save(commit=False)
            date_str = request.POST['deadline_date']
            time_str = request.POST['deadline_time']

            deadline_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            post.deadline = deadline_datetime
            post.user = request.user

            post.save()

            return redirect('top')
    return render(request, 'top.html', {'form': form})

def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        post.delete()
        return redirect('profile', user_id=post.user.id)
    return render(request, 'profile.html')

def delete_evidence(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        post.evidence.delete()
        return redirect('profile', user_id=post.user.id)
    return render(request, 'profile.html')

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
        if request.user != post.user:
            notification_content = f"「{request.user.username}」さんが宣言「{post.content}」にいいねしました"
            Notification.objects.create(user=post.user, post=post, content=notification_content)


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
            notification_content = f"「{request.user.username}」さんにフォローされました"
            Notification.objects.create(user=user_to_toggle, content=notification_content)

        response_data = {
            'success': True,
            'is_following': is_following
        }
    except CustomUser.DoesNotExist:
        pass

    return JsonResponse(response_data)

def get_follow_status(request, user_id):
    user_to_toggle = CustomUser.objects.get(id=user_id)
    follow_status = request.user.profile.follows.filter(id=user_to_toggle.profile.id).exists()
    return JsonResponse({'success': follow_status})

def evidence(request):
    if request.method == 'POST':
        form = EvidenceForm(request.POST)
        form_image = EvidenceImageForm(request.POST, request.FILES)

        if form.is_valid() and form_image.is_valid():
            post_id = request.POST.get('post_id')
            post = Post.objects.get(id=post_id)
            evidence = form.save(commit=False)
            evidence.user = request.user
            evidence.post = post
            evidence.save()
            images = request.FILES.getlist('image')
            for image in images:
                EvidenceImage.objects.create(evidence=evidence, image=image)
            return redirect('profile', user_id=request.user.id)
    else:
        form = EvidenceForm()
        form_image = EvidenceImageForm()
    return render(request, 'top.html', {'form': form, 'form_image': form_image})

def evidence_detail(request, evidence_id):
    evidence = get_object_or_404(Evidence, id=evidence_id)
    evidence_ratings = EvidenceRating.objects.filter(evidence_id=evidence.id).order_by('-timestamp')
    evidence.delta = human_readable_time_from_utc(evidence.timestamp)
    evidence.post.delta = human_readable_time_from_utc(evidence.post.timestamp)
    for evidence_rating in evidence_ratings:
        evidence_rating.delta = human_readable_time_from_utc(evidence_rating.timestamp)

    evidence_rate = EvidenceRating.objects.filter(evidence_id=evidence.id)
    user_has_rated = any(rating.user == request.user for rating in evidence_rate)

    if evidence_rate:
      average_rating = evidence_rate.aggregate(Avg('star_count'))
      rounded_avg = round(average_rating['star_count__avg'], 1)
    else:
        rounded_avg = 0

    context = {
      'evidence': evidence,
      'evidence_ratings': evidence_ratings,
      'user_has_rated': user_has_rated,
      'rounded_avg': rounded_avg,
    }
    return render(request, 'evidence_detail.html', context)

def submit_rating(request, evidence_id):
    if request.method == 'POST':
        form = EvidenceRatingForm(request.POST)
        evidence = Evidence.objects.get(id=evidence_id)
        if form.is_valid():
            star_count = form.cleaned_data['star_count']
            text = form.cleaned_data['text']
            EvidenceRating.objects.create(user=request.user, post=evidence.post, evidence=evidence,
                                              star_count=star_count, text=text)

            notification_content = f"「{request.user.username}」さんに提出した証拠の「{evidence.text}」を評価されました"
            Notification.objects.create(user=evidence.user, post=evidence.post, content=notification_content)
            return redirect('evidence_detail', evidence_id=evidence.id)
        else:
            form = EvidenceRatingForm()
        return render(request, 'evidence_detail.html', {'form': form})

def get_star_status(request):
    evidence_ratings = EvidenceRating.objects.all()
    response_data = {}
    for evidence in evidence_ratings:
        response_data[evidence.id] = evidence.star_count

    return JsonResponse(response_data)

def notification(request):
    user = request.user
    notifications = Notification.objects.filter(user=user).order_by('-timestamp')
    Notification.objects.filter(user=user, read=False).update(read=True)

    paginator = Paginator(notifications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'notification.html', {'page_obj':page_obj})

def check_new_notifications(request):
    user = request.user
    has_new_notifications = Notification.objects.filter(user=user, read=False).exists()

    response_data = {'hasNewNotification': has_new_notifications}
    return JsonResponse(response_data)

def search(request):
    return render(request, 'search.html')

def search_results(request):
    query = request.GET.get('search', '')

    matching_posts = Post.objects.filter(text__icontains=query)

    matching_evidences = Evidence.objects.filter(text__icontains=query)

    context = {
        'matching_posts': matching_posts,
        'matching_evidences': matching_evidences
    }
    return render(request, 'search.html', context)