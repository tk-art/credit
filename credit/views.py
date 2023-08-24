from django.shortcuts import render
from .forms import SignupForm, ProfileForm
from .models import CustomUser, Profile
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404


def top(request):
  return render(request, 'top.html')

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
    return render(request, 'profile.html', {'profile': profile})

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
