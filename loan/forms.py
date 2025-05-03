from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from .models import Customer
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Password'
        })
    )

class RegisterForm(forms.ModelForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Password'
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Confirm Password'
        })
    )
    
    dob = forms.DateField(
        input_formats=['%d.%m.%Y', '%Y-%m-%d'],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'dd.mm.yyyy',
            'maxlength': '10',
            'oninput': 'formatDateInput(this)',
            'autocomplete': 'off'
        }),
        label='Date of Birth'
    )

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+254700000000'. Up to 15 digits allowed."
    )

    phone_number = forms.CharField(
        validators=[phone_regex],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number (e.g. +254700000000)'
        })
    )

    class Meta:
        model = Customer
        fields = [
            'full_name', 
            'dob', 
            'id_number', 
            'phone_number', 
            'next_of_kin_name', 
            'next_of_kin_phone', 
            'employment_status'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Full Name'
            }),
            'id_number': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'ID Number'
            }),
            'next_of_kin_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Next of Kin Name'
            }),
            'next_of_kin_phone': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Next of Kin Phone'
            }),
            'employment_status': forms.Select(attrs={
                'class': 'form-control'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email is already registered.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords do not match.")

        return cleaned_data

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['email'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )
        customer = super().save(commit=False)
        customer.user = user
        if commit:
            customer.save()
        return customer

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            'full_name',
            'phone_number',
            'id_number',
            'dob',
            'next_of_kin_name',
            'next_of_kin_phone',
            'employment_status'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'id_number': forms.TextInput(attrs={'class': 'form-control'}),
            'dob': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'next_of_kin_name': forms.TextInput(attrs={'class': 'form-control'}),
            'next_of_kin_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'employment_status': forms.Select(attrs={'class': 'form-control'}),
        }

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )