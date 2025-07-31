from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

# @login_required
def index(request):
    # if request.user.is_teacher:
        return render(request, 't_homepage.html')
