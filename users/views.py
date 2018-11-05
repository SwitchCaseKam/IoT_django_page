from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import UserRegisterForm
from django.contrib.auth.decorators import login_required
from blog.models import Drinking, Activity


# Create your views here.
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created! You are now able to log in!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    context = {
        #'posts': Post.objects.all()
        #'stats': Stats.objects.all()
        #'tests': Test.objects.using('smartband_database').all(),
        'drinking': Drinking.objects.using('new_smartband_db').all(),
        'activity': Activity.objects.using('new_smartband_db').all()


    }
    return render(request, 'users/profile.html', context)
