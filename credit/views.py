from django.shortcuts import render

def top(request):
  return render(request, 'top.html')

def signup(request):
  return render(request, 'signup.html')
