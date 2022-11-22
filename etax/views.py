from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse


from django.shortcuts import render
from django.views import View
from django.http import HttpResponse

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout

from .models import User

from .utils import get_unique_tin

# Create your views here.

class IndexView(View):
    def get(self, request):
        title = 'Welcome'

        context = {
            'title': title,
        }
        # return HttpResponse("Home Page")
        return render(request, 'landing.html', context)

    def post(self, request):
        if 'login' in request.POST:
            context = {}
            username = request.POST['username']
            password = request.POST['password']

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('etax:landing')
            else:
                context['login_error'] = 'Invalid Credentials, try again!'
            return render(request, 'landing.html', context)

        if 'register' in request.POST:
            username = request.POST['email']
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            password = request.POST['password']

            print(username)

            new_user = User(
                username = username,
                email = username,
                first_name = first_name,
                last_name = last_name,
                tin = get_unique_tin(),
                is_payer = True
            )
            new_user.set_password(password)

            new_user.save()

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('etax:landing')
            return HttpResponse('unsuccessful')




def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
    return HttpResponseRedirect(reverse('etax:landing'))


class DashboardView(LoginRequiredMixin, View):
    login_url = '/'
    redirect_field_name = '/'

    def get(self, request):
        context = {
            'title': 'Dashboard'
        }
        return render(request, 'dashboard.html', context)

    def post(self, request):
        return HttpResponse("Dashboard")
