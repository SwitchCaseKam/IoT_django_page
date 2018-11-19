from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from .models import Post
from .models import Stats
from .models import Test
from .models import Drinking
from .models import Activity
from django.contrib.auth.decorators import login_required

from .visualizer import *

posts = [
    {
        'author': 'Kamil',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'October 17, 2018'
    },
    {
        'author': 'Borys',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'October 18, 2018'
    }
]
# Create your views here.
def home(request):
    current_user = User.objects.filter(username=request.user).first()
    if current_user is None:
        return render(request, 'blog/home.html', {})
    v = Visualizer(user=current_user.id)
    context = {
        #'posts': Post.objects.all()
        #'stats': Stats.objects.all()
        #'tests': Test.objects.using('smartband_database').all(),
        #'drinking' : Drinking.objects.using('new_smartband_db').order_by('-timestamp').all(),
        #'activity': Activity.objects.using('new_smartband_db').order_by('-timestamp').all(),
        'last_alcohol': v.plot_last_alcohol(),
        'last_steps': v.plot_last_steps(),
        'last_pulse': v.plot_last_pulse(),
        'monthly_alcohol': v.plot_monthly_alcohol(),
        'monthly_steps': v.plot_monthly_steps(),
        'monthly_pulse': v.plot_monthly_pulse(),
        'user_db_id': current_user.id
    }
    return render(request, 'blog/home.html', context)

@login_required
def analysis(request):
    current_user = User.objects.filter(username=request.user).first()
    if current_user is None:
        return render(request, 'blog/analysis.html', {})
    v = Visualizer(user=current_user.id)
    analysis = v.plot_analysis()
    context = {
        #'posts': Post.objects.all()
        #'stats': Stats.objects.all()
        #'tests': Test.objects.using('smartband_database').all(),
        #'drinking' : Drinking.objects.using('new_smartband_db').order_by('-timestamp').all(),
        #'activity': Activity.objects.using('new_smartband_db').order_by('-timestamp').all(),
        #'user_id': current_user_id,
        'alcohol': v.plot_alcohol(),
        'steps': v.plot_steps(),
        'pulse': v.plot_pulse(),
        'activity': v.plot_activity(),
        'analysis2d': analysis[0],
        'analysis3d': analysis[1],
        'user_db_id': current_user.id
    }
    return render(request, 'blog/analysis.html', context)

def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})
