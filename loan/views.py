from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib import messages
from .forms import RegisterForm, LoginForm, ProfileUpdateForm
from .models import Customer
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_backends
from django.contrib.auth.forms import PasswordChangeForm

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid email or password')
    else:
        form = LoginForm()
    return render(request, 'loan/login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            customer = form.save()
            user = customer.user
            backend = get_backends()[0]
            user.backend = f'{backend.__module__}.{backend.__class__.__name__}'
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'loan/register.html', {'form': form})

@login_required
def dashboard(request):
    customer = get_object_or_404(Customer, user=request.user)
    
    if customer.loan_limit == 0:
        customer.assign_loan_limit()
    
    processing_fee = customer.calculate_processing_fee()
    
    return render(request, 'loan/dashboard.html', {
        'customer': customer,
        'processing_fee': processing_fee,
        'payment_link': 'https://checkoutjpv2.jambopay.com/lipa/paybill/16525439'
    })

def home(request):
    return render(request, 'loan/home.html')

@login_required
def apply_loan(request):
    if request.method == 'POST':
        customer = get_object_or_404(Customer, user=request.user)
        messages.success(request, "Loan application submitted successfully!")
        return redirect('loan_status')
    return render(request, 'loan/apply_loan.html')

@login_required
def profile_view(request):
    customer = get_object_or_404(Customer, user=request.user)
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=customer)
    
    return render(request, 'loan/profile.html', {'form': form})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'loan/change_password.html', {'form': form})

@login_required
def loan_status(request):
    customer = get_object_or_404(Customer, user=request.user)
    return render(request, 'loan/status.html', {
        'customer': customer,
        'payment_link': "https://checkoutjpv2.jambopay.com/lipa/paybill/16525439"
    })

@login_required
def repayment(request):
    return render(request, 'loan/repayment.html')