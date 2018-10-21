from django.shortcuts import render
from django.http import HttpResponse
from .models import Post
from .models import Stats

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
    context = {
        #'posts': Post.objects.all()
        'stats': Stats.objects.all()
    }
    return render(request, 'blog/home.html', context)

def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})
