from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegistrationForm, TransactionForm
from .models import Account, Transaction

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Account.objects.create(user=user)
            login(request, user)
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def home(request):
    account = Account.objects.get(user=request.user)
    transactions = Transaction.objects.filter(account=account).order_by('-created_at')
    return render(request, 'accounts/home.html', {'account': account, 'transactions': transactions})

@login_required
def transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            account = Account.objects.get(user=request.user)
            transaction_type = form.cleaned_data['transaction_type']
            amount = form.cleaned_data['amount']
            if transaction_type == 'deposit':
                account.balance += amount
            elif transaction_type == 'withdraw' and account.balance >= amount:
                account.balance -= amount
            account.save()
            Transaction.objects.create(account=account, amount=amount, transaction_type=transaction_type)
            return redirect('home')
    else:
        form = TransactionForm()
    return render(request, 'accounts/transaction.html', {'form': form})
