from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse


from django.shortcuts import render
from django.views import View
from django.http import HttpResponse

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout

from .models import User, TaxPayment, Tcc, Address, Asset, AssetType

from .utils import get_unique_tin, process_payment

from datetime import date
from dateutil.relativedelta import relativedelta



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


class DashboardView(View):
    login_url = '/'
    redirect_field_name = '/'

    def get(self, request):
        title = 'Dashboard'
        assets = Asset.objects.filter(owner=request.user)
        assets_count = assets.count()
        payments = TaxPayment.objects.filter(asset__owner=request.user)
        asset_types = AssetType.objects.all()
        ast_types = {}
        for ast in asset_types:
            ast_types[ast.name] = ast.rate * 100
            # ast_types.append({'name': ast.name}, {'rate': ast.rate * 100})

        context = {
            'title': title,
            'assets_count': assets_count,
            'payments': payments,
            'asset_types': ast_types,
            'segment': ['dashboard'],
        }
        return render(request, 'dashboard.html', context)

    def post(self, request):
        return HttpResponse("Dashboard: post")


class TCCView(LoginRequiredMixin, View):
    login_url = '/'
    redirect_field_name = '/'

    def get(self, request):
        title = 'TCC'
        if request.user.is_staff:
            tccs = Tcc.objects.all()
        else:
            tccs = Tcc.objects.filter(owner=request.user)
        years = [i for i in range(2017, 2023)]

        context = {
            'title': title,
            'segment': ['tcc'],
            'years': years,
            'tccs': tccs,
        }
        return render(request, 'tcc.html', context)

    def post(self, request):
        start = request.POST['start']
        end = request.POST['end']

        tcc = Tcc()
        tcc.owner = request.user
        tcc.start = date(int(start), 1, 1)
        tcc.end = date(int(end), 12, 31)
        tcc.save()


        return HttpResponseRedirect(reverse('etax:tcc'))


class AssetsView(View):
    login_url = '/'
    redirect_field_name = '/'

    def get(self, request):
        title = 'Assets'
        assets = Asset.objects.filter(owner=request.user)
        asset_types = AssetType.objects.all()
        # fraud_count = transactions.filter(is_fraud=True).count()

        context = {
            'title': title,
            'assets': assets,
            'asset_types': asset_types,
            'asset_count': assets.count(),
            'segment': ['assets'],
        }
        return render(request, 'assets.html', context)

    def post(self, request):
        description = request.POST['description']
        price = request.POST['price']
        type_id = request.POST['type_id']

        ast = Asset()
        ast.owner = request.user
        ast.description = description
        ast.price = float(price)
        ast.asset_type_id = type_id
        ast.save()

        return HttpResponseRedirect(reverse('etax:assets'))


class PaymentView(LoginRequiredMixin, View):
    login_url = '/'
    redirect_field_name = '/'

    def get(self, request):
        title = 'Payments'
        payments = TaxPayment.objects.filter(asset__owner=request.user)

        context = {
            'title': title,
            'payments': payments,
            'segment': ['payments'],
        }
        return render(request, 'payments.html', context)

    def post(self, request):
        return HttpResponse("Payment: post")


class MakePaymentView(LoginRequiredMixin, View):
    login_url = '/'
    redirect_field_name = '/'

    def get(self, request, asset_id):
        title = 'Payments'
        asset = Asset.objects.get(id=asset_id)
        context = {
            'title': title,
            'asset': asset,
            'segment': ['payments'],
        }
        return render(request, 'make_payment.html', context)

    def post(self, request, asset_id):
        asset = Asset.objects.get(id=asset_id)
        
        tx = TaxPayment()
        tx.asset_id = asset_id
        tx.amount = asset.tax_amount

        if process_payment():
            asset.tax_paid = True
            tx.is_successful = True
        asset.save()
        tx.save()
        return HttpResponseRedirect(reverse('etax:assets'))


class AdminDashboardView(LoginRequiredMixin, View):
    login_url = '/'
    redirect_field_name = '/'

    def get(self, request):
        if not request.user.is_staff:
            return HttpResponseRedirect(reverse('etax:home'))
        title = 'Admin Dashboard'
        assets = Asset.objects.all()
        payments = TaxPayment.objects.all().order_by('-date')
        asset_types = AssetType.objects.all()
        ast_types = {}
        for ast in asset_types:
            ast_types[ast.name] = ast.rate * 100
        

        d = date.today()
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        days_date = [d - relativedelta(days = x) for x in range(8)]


        labels = {
            days[x.weekday()]: get_total_per_day(
                TaxPayment.objects.filter(
                    date__year=x.year,
                    date__month=x.month,
                    date__day=x.day,
                    is_successful=True
                    )) for x in days_date
        }

        

        x_labels = [x for x,y in labels.items()]
        y_labels = [y for x,y in labels.items()]

        today_total = 0
        for amount in y_labels:
            today_total += amount

        # print(x_labels)
        # print(y_labels)
        # for day, amount in labels.items():
        #     print(day, amount)
        x_labels.reverse()
        y_labels.reverse()

        card_items = {
            'Individuals': User.objects.filter(user_type='IND').count(),
            'Businesses': User.objects.filter(user_type='BIZ').count(),
            'Cleared Assets': assets.filter(tax_paid=True).count(),
            'Pending TCC Requests': Tcc.objects.filter(is_approved=False).count(),
        }

        context = {
            'title': title,
            'payments': payments,
            'asset_types': ast_types,
            'segment': ['dashboard'],
            'card_items': card_items,
            'x_labels': x_labels,
            'y_labels': y_labels,
            'today_amount': today_total,
        }
        return render(request, 'dashboard.html', context)

    def post(self, request):
        return HttpResponse("Dashboard: post")


class DeleteTccView(LoginRequiredMixin, View):
    login_url = '/'
    redirect_field_name = '/'

    def get(self, request, tcc_id):
        tcc = Tcc.objects.get(id=tcc_id)
        tcc.delete()
        return HttpResponseRedirect(reverse('etax:tcc'))

class ApproveTccView(LoginRequiredMixin, View):
    login_url = '/'
    redirect_field_name = '/'

    def get(self, request, tcc_id):
        tcc = Tcc.objects.get(pk=tcc_id)
        tcc.is_approved = True
        tcc.save()
        return HttpResponseRedirect(reverse('etax:tcc'))


def get_total_per_day(queryset):
    sum = 0
    for tx in queryset:
        sum += tx.amount
    return sum